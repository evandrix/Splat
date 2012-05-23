#include "Python.h"
#include "JIT/RuntimeFeedback.h"

#include "llvm/ADT/PointerIntPair.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/SmallVector.h"

#include <algorithm>

using llvm::PointerIntPair;
using llvm::PointerLikeTypeTraits;
using llvm::SmallPtrSet;
using llvm::SmallVector;


PyLimitedFeedback::PyLimitedFeedback()
{
}

PyLimitedFeedback::PyLimitedFeedback(const PyLimitedFeedback &src)
{
    for (int i = 0; i < PyLimitedFeedback::NUM_POINTERS; ++i) {
        if (src.InObjectMode()) {
            PyObject *value = (PyObject *)src.data_[i].getPointer();
            Py_XINCREF(value);
            this->data_[i] = src.data_[i];
        }
        else {
            this->data_[i] = src.data_[i];
        }
    }
}

PyLimitedFeedback::~PyLimitedFeedback()
{
    this->Clear();
}

PyLimitedFeedback &
PyLimitedFeedback::operator=(PyLimitedFeedback rhs)
{
    this->Swap(&rhs);
    return *this;
}

void
PyLimitedFeedback::Swap(PyLimitedFeedback *other)
{
    for (int i = 0; i < PyLimitedFeedback::NUM_POINTERS; ++i) {
        std::swap(this->data_[i], other->data_[i]);
    }
}

void
PyLimitedFeedback::SetFlagBit(unsigned index, bool value)
{
    assert(index < 6);
    PointerIntPair<void*, 2>& slot = this->data_[index / 2];
    unsigned mask = 1 << (index % 2);
    unsigned old_value = slot.getInt();
    unsigned new_value = (old_value & ~mask) | (value << (index % 2));
    slot.setInt(new_value);
}

bool
PyLimitedFeedback::GetFlagBit(unsigned index) const
{
    assert(index < 6);
    const PointerIntPair<void*, 2>& slot = this->data_[index / 2];
    unsigned value = slot.getInt();
    return (value >> (index % 2)) & 1;
}

void
PyLimitedFeedback::IncCounter(unsigned counter_id)
{
    assert(this->InCounterMode());
    assert(counter_id < (unsigned)PyLimitedFeedback::NUM_POINTERS);
    this->SetFlagBit(COUNTER_MODE_BIT, true);

    uintptr_t old_value =
        reinterpret_cast<uintptr_t>(this->data_[counter_id].getPointer());
    uintptr_t shift = PointerLikeTypeTraits<PyObject*>::NumLowBitsAvailable;
    uintptr_t new_value = old_value + (1U << shift);
    if (new_value > old_value) {
        // Only increment if we're not saturated yet.
        this->data_[counter_id].setPointer(
            reinterpret_cast<void*>(new_value));
    }
}

uintptr_t
PyLimitedFeedback::GetCounter(unsigned counter_id) const
{
    assert(this->InCounterMode());

    uintptr_t shift = PointerLikeTypeTraits<PyObject*>::NumLowBitsAvailable;
    void *counter_as_pointer = this->data_[counter_id].getPointer();
    return reinterpret_cast<uintptr_t>(counter_as_pointer) >> shift;
}

void
PyLimitedFeedback::Clear()
{
    bool object_mode = this->InObjectMode();

    for (int i = 0; i < PyLimitedFeedback::NUM_POINTERS; ++i) {
        if (object_mode) {
            Py_XDECREF((PyObject *)this->data_[i].getPointer());
        }
        this->data_[i].setPointer(NULL);
        this->data_[i].setInt(0);
    }
}

void
PyLimitedFeedback::AddObjectSeen(PyObject *obj)
{
    assert(this->InObjectMode());
    this->SetFlagBit(OBJECT_MODE_BIT, true);

    if (obj == NULL) {
        SetFlagBit(SAW_A_NULL_OBJECT_BIT, true);
        return;
    }
    for (int i = 0; i < PyLimitedFeedback::NUM_POINTERS; ++i) {
        PyObject *value = (PyObject *)data_[i].getPointer();
        if (value == obj)
            return;
        if (value == NULL) {
            Py_INCREF(obj);
            data_[i].setPointer((void *)obj);
            return;
        }
    }
    // Record overflow.
    SetFlagBit(SAW_MORE_THAN_THREE_OBJS_BIT, true);
}

void
PyLimitedFeedback::GetSeenObjectsInto(SmallVector<PyObject*, 3> &result) const
{
    assert(this->InObjectMode());

    result.clear();
    if (GetFlagBit(SAW_A_NULL_OBJECT_BIT)) {
        // Saw a NULL value, so add NULL to the result.
        result.push_back(NULL);
    }
    for (int i = 0; i < PyLimitedFeedback::NUM_POINTERS; ++i) {
        PyObject *value = (PyObject *)data_[i].getPointer();
        if (value == NULL)
            return;
        result.push_back(value);
    }
}

void
PyLimitedFeedback::AddFuncSeen(PyObject *obj)
{
    assert(this->InFuncMode());
    this->SetFlagBit(FUNC_MODE_BIT, true);

    if (this->GetFlagBit(SAW_MORE_THAN_THREE_OBJS_BIT))
        return;
    if (obj == NULL) {
        this->SetFlagBit(SAW_A_NULL_OBJECT_BIT, true);
        return;
    }

    // Record the type of the function, and the methoddef if it's a call to a C
    // function.
    PyTypeObject *type = Py_TYPE(obj);
    PyMethodDef *ml = NULL;
    if (PyCFunction_Check(obj)) {
        ml = PyCFunction_GET_METHODDEF(obj);
    } else if (PyMethodDescr_Check(obj)) {
        ml = ((PyMethodDescrObject *)obj)->d_method;
    }

    PyTypeObject *old_type = (PyTypeObject *)this->data_[0].getPointer();
    PyMethodDef *old_ml = (PyMethodDef *)this->data_[1].getPointer();
    if (old_type == NULL) {
        // Record this method.
        Py_INCREF(type);
        this->data_[0].setPointer((void*)type);
        this->data_[1].setPointer((void*)ml);
    } else if (old_type != type || old_ml != ml) {
        // We found something else here already.  Set this flag to indicate the
        // call site is polymorphic, even if we haven't seen more than three
        // objects.
        this->SetFlagBit(SAW_MORE_THAN_THREE_OBJS_BIT, true);
    }
    // The call site is monomorphic, so we leave it as is.
}

void
PyLimitedFeedback::GetSeenFuncsInto(
    SmallVector<PyTypeMethodPair, 3> &result) const
{
    assert(this->InFuncMode());

    result.clear();
    if (this->GetFlagBit(SAW_A_NULL_OBJECT_BIT)) {
        // Saw a NULL value, so add NULL to the result.
        result.push_back(
            std::make_pair<PyTypeObject*, PyMethodDef*>(NULL, NULL));
    }
    PyTypeObject *type = (PyTypeObject *)this->data_[0].getPointer();
    PyMethodDef *ml = (PyMethodDef *)this->data_[1].getPointer();
    result.push_back(std::make_pair<PyTypeObject*, PyMethodDef*>(type, ml));
}


PyFullFeedback::PyFullFeedback()
    : counters_(/* Zero out the array. */),
      usage_(UnknownMode)
{
}

PyFullFeedback::PyFullFeedback(const PyFullFeedback &src)
{
    this->usage_ = src.usage_;
    for (unsigned i = 0; i < llvm::array_lengthof(this->counters_); ++i)
        this->counters_[i] = src.counters_[i];
    for (ObjSet::iterator it = src.data_.begin(), end = src.data_.end();
            it != end; ++it) {
        void *obj = *it;
        if (src.usage_ == ObjectMode) {
            Py_XINCREF((PyObject *)obj);
        }
        else if (src.InFuncMode()) {
            PyTypeMethodPair &src_pair_ref = *(PyTypeMethodPair*)obj;
            obj = new PyTypeMethodPair(src_pair_ref);
        }
        this->data_.insert(obj);
    }
}

PyFullFeedback::~PyFullFeedback()
{
    if (this->InFuncMode()) {
        // We have to free these pairs if we're in func mode.
        for (ObjSet::const_iterator it = this->data_.begin(),
                end = this->data_.end(); it != end; ++it) {
            delete (PyTypeMethodPair*)*it;
        }
    }
    this->Clear();
}

PyFullFeedback &
PyFullFeedback::operator=(PyFullFeedback rhs)
{
    this->Swap(&rhs);
    return *this;
}

void
PyFullFeedback::Swap(PyFullFeedback *other)
{
    std::swap(this->usage_, other->usage_);
    std::swap(this->data_, other->data_);
    for (unsigned i = 0; i < llvm::array_lengthof(this->counters_); ++i)
        std::swap(this->counters_[i], other->counters_[i]);
}

void
PyFullFeedback::Clear()
{
    for (ObjSet::iterator it = this->data_.begin(),
            end = this->data_.end(); it != end; ++it) {
        if (this->usage_ == ObjectMode) {
            Py_XDECREF((PyObject *)*it);
        }
    }
    this->data_.clear();
    for (unsigned i = 0; i < llvm::array_lengthof(this->counters_); ++i)
        this->counters_[i] = 0;
    this->usage_ = UnknownMode;
}

void
PyFullFeedback::AddObjectSeen(PyObject *obj)
{
    assert(this->InObjectMode());
    this->usage_ = ObjectMode;

    if (obj == NULL) {
        this->data_.insert(NULL);
        return;
    }

    if (!this->data_.count(obj)) {
        Py_INCREF(obj);
        this->data_.insert((void *)obj);
    }
}

void
PyFullFeedback::GetSeenObjectsInto(
    SmallVector<PyObject*, /*in-object elems=*/3> &result) const
{
    assert(this->InObjectMode());

    result.clear();
    for (ObjSet::const_iterator it = this->data_.begin(),
             end = this->data_.end(); it != end; ++it) {
        result.push_back((PyObject *)*it);
    }
}

void
PyFullFeedback::AddFuncSeen(PyObject *obj)
{
    assert(this->InFuncMode());
    this->usage_ = FuncMode;

    PyMethodDef *ml = NULL;
    PyTypeObject *type = NULL;
    if (obj != NULL) {
        type = Py_TYPE(obj);

        // We only record a methoddef if this is a C function.
        if (PyCFunction_Check(obj)) {
            ml = PyCFunction_GET_METHODDEF(obj);
        } else if (PyMethodDescr_Check(obj)) {
            ml = ((PyMethodDescrObject *)obj)->d_method;
        }
    }

    for (ObjSet::const_iterator it = this->data_.begin(),
            end = this->data_.end(); it != end; ++it) {
        PyTypeMethodPair *pair = (PyTypeMethodPair*)*it;
        if (pair->first == type && pair->second == ml)
            return;
    }

    PyTypeMethodPair *pair = new PyTypeMethodPair(type, ml);
    this->data_.insert((void *)pair);
}

void
PyFullFeedback::GetSeenFuncsInto(
    SmallVector<PyTypeMethodPair, 3> &result) const
{
    assert(this->InFuncMode());

    result.clear();
    for (ObjSet::const_iterator it = this->data_.begin(),
            end = this->data_.end(); it != end; ++it) {
        result.push_back(*((PyTypeMethodPair *)*it));
    }
}

void
PyFullFeedback::IncCounter(unsigned counter_id)
{
    assert(this->InCounterMode());
    assert(counter_id < llvm::array_lengthof(this->counters_));
    this->usage_ = CounterMode;

    uintptr_t old_value = this->counters_[counter_id];
    uintptr_t new_value = old_value + 1;
    if (new_value > old_value) {
        // Only increment if we're not saturated yet.
        this->counters_[counter_id] = new_value;
    }
}

uintptr_t
PyFullFeedback::GetCounter(unsigned counter_id) const
{
    assert(this->InCounterMode());

    return this->counters_[counter_id];
}

PyFeedbackMap *
PyFeedbackMap_New()
{
    return new PyFeedbackMap;
}

void
PyFeedbackMap_Del(PyFeedbackMap *map)
{
    delete map;
}

void
PyFeedbackMap_Clear(PyFeedbackMap *map)
{
    map->Clear();
}

const PyRuntimeFeedback *
PyFeedbackMap::GetFeedbackEntry(unsigned opcode_index, unsigned arg_index) const
{
    llvm::DenseMap<std::pair<unsigned, unsigned>,
                   PyRuntimeFeedback>::const_iterator result =
        this->entries_.find(std::make_pair(opcode_index, arg_index));
    if (result == this->entries_.end())
        return NULL;
    return &result->second;
}

PyRuntimeFeedback &
PyFeedbackMap::GetOrCreateFeedbackEntry(
    unsigned opcode_index, unsigned arg_index)
{
    return this->entries_[std::make_pair(opcode_index, arg_index)];
}

void
PyFeedbackMap::Clear()
{
    for (FeedbackMap::iterator it = this->entries_.begin(),
            end = this->entries_.end(); it != end; ++it) {
        it->second.Clear();
    }
}
