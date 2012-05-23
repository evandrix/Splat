// -*- C++ -*-
#ifndef UTIL_TBALIASANALYSIS_H
#define UTIL_TBALIASANALYSIS_H

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Pass.h"

// Type based Alias Analysis Pass
llvm::Pass *CreatePyTBAliasAnalysis(struct PyGlobalLlvmData &global_data);

// A Pass to mark some function return values with types
llvm::Pass *CreatePyTypeMarkingPass(struct PyGlobalLlvmData &global_data);

// A Pass to remove some guards on type information
llvm::Pass *CreatePyTypeGuardRemovalPass(struct PyGlobalLlvmData &global_data);

#endif
