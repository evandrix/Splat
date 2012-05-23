// -*- C++ -*-
#ifndef UTIL_INSTRUMENTATION_H_
#define UTIL_INSTRUMENTATION_H_

#ifdef Py_WITH_INSTRUMENTATION

#include "llvm/Support/raw_ostream.h"

using llvm::errs;

// C++ requires template parameters to have external linkage.
// Global const char[] default to static, so we have to force it.
//
// eg.
// extern const char name[], shortname[];
// const char name[] = "SomeName";
// const char shortname = "Name";
//
// OpStats<name, shortname> FooStats;

template<const char* full_name, const char* short_name>
class OpStats {
public:
    OpStats()
        : total(0), optimized(0), unpredictable(0), omitted(0) {
    }

    ~OpStats() {
        errs() << "\n" << full_name << " inlining:\n";
        errs() << "Total " << short_name << ": " << this->total << "\n";
        errs() << "Optimized " << short_name << ": " << this->optimized << "\n";
        errs() << "Unpredictable types: " << this->unpredictable << "\n";
        errs() << short_name << " without inline version: " <<
            this->omitted << "\n";
    }

    // Total number of binary opcodes compiled.
    unsigned total;
    // Number of opcodes inlined.
    unsigned optimized;
    // Number of opcodes with unpredictable types.
    unsigned unpredictable;
    // Number of opcodes without inline-able functions.
    unsigned omitted;
};

#endif /* Py_WITH_INSTRUMENTATION */
#endif /* UTIL_INSTRUMENTATION_H_ */
