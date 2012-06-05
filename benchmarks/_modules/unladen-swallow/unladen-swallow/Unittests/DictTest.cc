#include "Python.h"
#include "gtest/gtest.h"

class DictWatcherTest : public testing::Test {
protected:
    DictWatcherTest()
    {
        Py_NoSiteFlag = true;
        Py_Initialize();
        this->globals_ = PyDict_New();
        this->builtins_ = PyDict_New();
    }
    ~DictWatcherTest()
    {
        Py_DECREF(this->globals_);
        Py_DECREF(this->builtins_);
        Py_Finalize();
    }

    // Satisfying all the inputs to PyCode_New() is hard, so we fake it.
    // You will need to PyMem_DEL the result manually.
    PyCodeObject *FakeCodeObject()
    {
        PyCodeObject *code = PyMem_NEW(PyCodeObject, 1);
        assert(code != NULL);
        // We only initialize the fields related to dict watchers.
        code->co_watching = NULL;
        code->co_use_jit = 0;
        code->co_fatalbailcount = 0;
        code->ob_type = &PyCode_Type;
        return code;
    }

    PyObject *globals_;
    PyObject *builtins_;
};

TEST_F(DictWatcherTest, AddWatcher)
{
    PyCodeObject *code = this->FakeCodeObject();

    _PyDict_AddWatcher(this->globals_, code);

    PyDictObject *dict = (PyDictObject *)this->globals_;
    EXPECT_EQ(1, _PyDict_NumWatchers(dict));

    // Drop the watcher to prevent the dict's dealloc from referencing freed
    // memory.
    _PyDict_DropWatcher(this->globals_, code);
    PyMem_DEL(code);
}

// _PyDict_DropWatcher() used to leave holes in the watcher array. This test
// verifies that DropWatcher() compacts the array.
TEST_F(DictWatcherTest, DropWatcherAddWatcherSequence)
{
    PyCodeObject *code1 = this->FakeCodeObject();
    PyCodeObject *code2 = this->FakeCodeObject();

    _PyDict_AddWatcher(this->globals_, code1);
    _PyDict_AddWatcher(this->globals_, code2);
    _PyDict_DropWatcher(this->globals_, code1);

    PyDictObject *dict = (PyDictObject *)this->globals_;
    EXPECT_EQ(1, _PyDict_NumWatchers(dict));
    EXPECT_TRUE(_PyDict_IsWatchedBy(dict, code2));

    _PyDict_DropWatcher(this->globals_, code2);
    PyMem_DEL(code1);
    PyMem_DEL(code2);
}

TEST_F(DictWatcherTest, DictDealloc)
{
    PyObject *globals = PyDict_New();
    PyObject *builtins = PyDict_New();
    PyCodeObject *code1 = this->FakeCodeObject();
    code1->co_use_jit = 1;

    EXPECT_EQ(0, _PyCode_WatchDict(code1, WATCHING_GLOBALS, globals));
    EXPECT_EQ(0, _PyCode_WatchDict(code1, WATCHING_BUILTINS, builtins));
    EXPECT_EQ(2, _PyCode_WatchingSize(code1));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)globals));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)builtins));

    // This will notify the dicts.
    Py_DECREF(globals);
    EXPECT_EQ(0, code1->co_use_jit);
    EXPECT_EQ(0, _PyCode_WatchingSize(code1));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)globals));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)builtins));

    Py_DECREF(builtins);
    PyMem_DEL(code1);
}

TEST_F(DictWatcherTest, NotifyWatcher)
{
    PyCodeObject *code1 = this->FakeCodeObject();
    code1->co_use_jit = 1;

    EXPECT_EQ(0, _PyCode_WatchDict(code1, WATCHING_GLOBALS, this->globals_));
    EXPECT_EQ(0, _PyCode_WatchDict(code1, WATCHING_BUILTINS, this->builtins_));
    EXPECT_EQ(1, code1->co_use_jit);

    // This should notify the watchers.
    PyDict_SetItemString(this->globals_, "hello", Py_None);

    EXPECT_EQ(0, code1->co_use_jit);
    PyDictObject *globals_dict = (PyDictObject *)this->globals_;
    EXPECT_EQ(0, _PyDict_NumWatchers(globals_dict));
    PyDictObject *builtins_dict = (PyDictObject *)this->builtins_;
    EXPECT_EQ(0, _PyDict_NumWatchers(builtins_dict));

    EXPECT_EQ(0, _PyCode_WatchingSize(code1));

    PyMem_DEL(code1);
}
