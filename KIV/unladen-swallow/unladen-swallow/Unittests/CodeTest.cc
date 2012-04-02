#include "Python.h"
#include "gtest/gtest.h"

class CodeWatchingTest : public testing::Test {
protected:
    CodeWatchingTest()
    {
        Py_NoSiteFlag = true;
        Py_Initialize();
        this->globals_ = PyDict_New();
        this->builtins_ = PyDict_New();
    }
    ~CodeWatchingTest()
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

TEST_F(CodeWatchingTest, WatchDict)
{
    PyCodeObject *code = this->FakeCodeObject();

    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    _PyCode_WatchDict(code, WATCHING_GLOBALS, this->globals_);
    EXPECT_EQ(1, _PyCode_WatchingSize(code));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    // Same dict, same slot, same code object.
    _PyCode_WatchDict(code, WATCHING_GLOBALS, this->globals_);
    EXPECT_EQ(1, _PyCode_WatchingSize(code));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    // Different dict, different slot.
    _PyCode_WatchDict(code, WATCHING_BUILTINS, this->builtins_);
    EXPECT_EQ(2, _PyCode_WatchingSize(code));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    _PyCode_IgnoreWatchedDicts(code);
    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    PyMem_DEL(code);
}

TEST_F(CodeWatchingTest, RepeatedIgnore)
{
    PyCodeObject *code = this->FakeCodeObject();

    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    _PyCode_WatchDict(code, WATCHING_GLOBALS, this->globals_);
    EXPECT_EQ(1, _PyCode_WatchingSize(code));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    _PyCode_IgnoreWatchedDicts(code);
    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    // Do it again, don't blow up.
    _PyCode_IgnoreWatchedDicts(code);
    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    PyMem_DEL(code);
}

TEST_F(CodeWatchingTest, IgnoreDict)
{
    PyCodeObject *code = this->FakeCodeObject();
    EXPECT_EQ(0, _PyCode_WatchingSize(code));

    // Ignore un-watched dict.
    EXPECT_EQ(0, _PyCode_IgnoreDict(code, WATCHING_GLOBALS));
    EXPECT_EQ(0, _PyCode_IgnoreDict(code, WATCHING_BUILTINS));

    // Add both dicts.
    _PyCode_WatchDict(code, WATCHING_GLOBALS, this->globals_);
    _PyCode_WatchDict(code, WATCHING_BUILTINS, this->builtins_);
    EXPECT_EQ(2, _PyCode_WatchingSize(code));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    // Ignore one of them.
    EXPECT_EQ(0, _PyCode_IgnoreDict(code, WATCHING_GLOBALS));
    EXPECT_EQ(1, _PyCode_WatchingSize(code));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    // Now ignore the other one.
    EXPECT_EQ(0, _PyCode_IgnoreDict(code, WATCHING_BUILTINS));
    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    PyMem_DEL(code);
}

TEST_F(CodeWatchingTest, InvalidateMachineCode)
{
    PyCodeObject *code = this->FakeCodeObject();
    EXPECT_EQ(0, code->co_fatalbailcount);

    // Fake our way through compilation.
    code->co_use_jit = 1;
    _PyCode_WatchDict(code, WATCHING_GLOBALS, this->globals_);
    _PyCode_WatchDict(code, WATCHING_BUILTINS, this->builtins_);
    EXPECT_EQ(2, _PyCode_WatchingSize(code));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(1, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    _PyCode_InvalidateMachineCode(code);
    EXPECT_EQ(1, code->co_fatalbailcount);
    EXPECT_EQ(0, code->co_use_jit);
    EXPECT_EQ(0, _PyCode_WatchingSize(code));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->globals_));
    EXPECT_EQ(0, _PyDict_NumWatchers((PyDictObject *)this->builtins_));

    PyMem_DEL(code);
}

