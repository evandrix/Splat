#include "Util/PySmallPtrSet.h"
#include "gtest/gtest.h"


TEST(PySmallPtrSet, Basic)
{
    PySmallPtrSet *set = PySmallPtrSet_New();
    ASSERT_TRUE(set != NULL);
    EXPECT_EQ(0u, PySmallPtrSet_Size(set));

    PyObject *five = (PyObject *)5;
    PyObject *six = (PyObject *)6;
    EXPECT_EQ(1, PySmallPtrSet_Insert(set, five));
    EXPECT_EQ(1u, PySmallPtrSet_Size(set));

    // Insert additional element; size goes up.
    EXPECT_EQ(1, PySmallPtrSet_Insert(set, six));
    EXPECT_EQ(2u, PySmallPtrSet_Size(set));

    // Insert duplicate element; size unchanged.
    EXPECT_EQ(0, PySmallPtrSet_Insert(set, five));
    EXPECT_EQ(2u, PySmallPtrSet_Size(set));

    // Erase elements.
    EXPECT_EQ(1, PySmallPtrSet_Erase(set, five));
    EXPECT_EQ(1, PySmallPtrSet_Erase(set, six));
    EXPECT_EQ(0u, PySmallPtrSet_Size(set));

    // Erase missing element.
    EXPECT_EQ(0, PySmallPtrSet_Erase(set, five));

    PySmallPtrSet_Del(set);
}


static void
my_iter_func(PyObject *obj, void *counter)
{
    (*(int *)counter) += 2;
}

TEST(PySmallPtrSet, Iteration)
{
    int counter = 0;

    PySmallPtrSet *set = PySmallPtrSet_New();
    ASSERT_TRUE(set != NULL);

    PyObject *five = (PyObject *)5;
    PyObject *six = (PyObject *)6;
    EXPECT_EQ(1, PySmallPtrSet_Insert(set, five));
    EXPECT_EQ(1, PySmallPtrSet_Insert(set, six));

    PySmallPtrSet_ForEach(set, my_iter_func, &counter);
    EXPECT_EQ(4, counter);

    PySmallPtrSet_Del(set);
}
