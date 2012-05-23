from peak.api import *
from transactions import TransactionComponent
from peak.naming.factories.openable import FileFactory
import os, os.path

__all__ = ['TxnFile', 'EditableFile']

class TxnFile(TransactionComponent, FileFactory):

    """Transacted file (stream factory)"""

    isDeleted = False
    txnAttrs  = TransactionComponent.txnAttrs + ('isDeleted',)
    tmpName   = binding.Make( lambda self: self.filename+'.$$$' )


    def _txnInProgress(self):
        raise exceptions.TransactionInProgress(
            "Can't use autocommit with transaction in progress"
        )


    def delete(self, autocommit=False):

        if self.inTransaction:

            if autocommit:
                self._txnInProgress()   # can't use ac in txn

            if not self.isDeleted:
                os.unlink(self.tmpName)
                self.isDeleted = True

        elif autocommit:
            os.unlink(self.filename)

        else:
            # Neither autocommit nor txn, join txn and set deletion flag
            self.joinedTxn
            self.isDeleted = True

    def _open(self, mode, flags, ac):

        if mode not in ('t','b','U'):
            raise TypeError("Invalid open mode:", mode)

        elif self.inTransaction:

            if ac:
                self._txnInProgress()

            return open(self.tmpName, flags+mode)

        # From here down, we're not currently in a transaction...

        elif ac or flags=='r':
            # If we're reading, just read the original file
            # Or if autocommit, then also okay to use original file
            return open(self.filename, flags+mode)

        elif '+' in flags and 'w' not in flags:
            # Ugh, punt for now
            raise NotImplementedError(
                "Mixed-mode (read/write) access not supported w/out autocommit"
            )
        else:
            # Join the transaction first
            self.joinedTxn

            # Since we're always creating the file here, we don't use 'a'
            # mode.  We want to be sure to erase any stray contents left over
            # from another transaction.  XXX Note that this isn't safe for
            # a multiprocess environment!  We should use a lockfile.
            stream = open(self.tmpName, flags.replace('a','w')+mode)
            self.isDeleted = False
            return stream






    def exists(self):

        if self.inTransaction:
            return not self.isDeleted

        return os.path.exists(self.filename)


    def commitTransaction(self, txnService):

        if self.isDeleted:
            os.unlink(self.filename)
            return

        try:
            os.rename(self.tmpName, self.filename)

        except OSError:
            # Windows can't do this atomically.  :(  Better hope we don't
            # crash between these two operations, or somebody'll have to clean
            # up the mess.
            os.unlink(self.filename)
            os.rename(self.tmpName, self.filename)


    def abortTransaction(self, txnService):
        if not self.isDeleted:
            os.unlink(self.tmpName)













class EditableFile(TxnFile):
    """File whose text can be manipulated, transactionally

    Example::

        myfile = EditableFile(self, filename="something")
        print myfile.text   # prints current contents of file

        # Edit the file
        storage.beginTransaction(self)
        myfile.text = myfile.text.replace('foo','bar')
        storage.commitTransaction(self)

    Values assigned to 'text' will be converted to strings.  Setting 'text'
    to an empty string truncates the file; deleting 'text' (i.e.
    'del myfile.text') deletes the file.  'text' will be 'None' whenever the
    file is nonexistent, but do not set it to 'None' unless you want to replace
    the file's contents with the string '"None"'!

    By default, files are read and written in "text" mode; be sure to supply
    a 'fileType="b"' keyword argument if you are editing a binary file.  Note
    that under Python 2.3 you can also specify 'fileType="U"' to use "universal
    newline" mode.

    'EditableFile' subclasses 'TxnFile', but does not use 'autocommit' mode,
    because it wants to support "safe" alterations to existing files."""

    fileType = 't'
    outStream = None

    def __text(self):
        if self.exists():
            stream = self.open(self.fileType)
            try:
                return stream.read()
            finally:
                stream.close()
        # else return None

    __text = binding.Make(__text)

    def __setText(self, text):
        text = str(text)
        if self.__text == text:
            return
        if self.outStream is None:
            self.outStream = self.create(self.fileType) # joins txn
        self.__text = text

    def delete(self, autocommit=False):
        self.__close(False)
        self.__text = None
        super(EditableFile,self).delete(autocommit)

    text = property(lambda self:self.__text, __setText, delete)

    del __setText


    def __close(self, write=True):
        if self.outStream is not None:
            if write:
                self.outStream.write(self.__text)
            self.outStream.close()
            del self.outStream

    def voteForCommit(self, txnService):
        # Make sure we can at least write our data
        self.__close(not self.isDeleted)

    def abortTransaction(self, txnService):
        self.__close(False)
        super(EditableFile,self).abortTransaction(txnService)

    def finishTransaction(self, txnService, committed):
        # Ensure text is reloaded for next transaction
        self._delBinding('_EditableFile__text')
        super(EditableFile,self).finishTransaction(txnService, committed)




