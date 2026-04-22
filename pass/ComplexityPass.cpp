#include "llvm/IR/PassManager.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Type.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/LoopAnalysisManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include <set>

using namespace llvm;

// Recursively find max loop nesting depth
static int getMaxLoopDepth(Loop *L) {
    int maxDepth = L->getLoopDepth();
    for (Loop *SubL : L->getSubLoops()) {
        int d = getMaxLoopDepth(SubL);
        if (d > maxDepth) maxDepth = d;
    }
    return maxDepth;
}

// Walk type graph and count unique type nodes
static void collectTypeNodes(Type *T, std::set<Type*> &visited) {
    if (!T || visited.count(T)) return;
    visited.insert(T);
    if (auto *ST = dyn_cast<StructType>(T)) {
        for (unsigned i = 0; i < ST->getNumElements(); i++)
            collectTypeNodes(ST->getElementType(i), visited);
    } else if (auto *AT = dyn_cast<ArrayType>(T)) {
        collectTypeNodes(AT->getElementType(), visited);
    } else if (auto *FT = dyn_cast<FunctionType>(T)) {
        collectTypeNodes(FT->getReturnType(), visited);
        for (unsigned i = 0; i < FT->getNumParams(); i++)
            collectTypeNodes(FT->getParamType(i), visited);
    } else if (auto *VT = dyn_cast<VectorType>(T)) {
        collectTypeNodes(VT->getElementType(), visited);
    }
}

struct ComplexityPass : public PassInfoMixin<ComplexityPass> {

    // Declare that we need LoopAnalysis
    static bool isRequired() { return true; }

    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        // Skip external declarations
        if (F.isDeclaration() || F.empty())
            return PreservedAnalyses::all();

        // 1. Instruction count
        int instrCount = 0;
        for (auto &BB : F)
            instrCount += (int)BB.size();

        // 2. Basic block count
        int bbCount = (int)F.size();

        // 3. Loop nest depth — recursive walk
        int loopDepth = 0;
        auto &LI = FAM.getResult<LoopAnalysis>(F);
        for (Loop *L : LI) {
            int d = getMaxLoopDepth(L);
            if (d > loopDepth) loopDepth = d;
        }

        // 4. PHI node count
        int phiCount = 0;
        for (auto &BB : F)
            for (auto &I : BB)
                if (isa<PHINode>(I)) phiCount++;

        // 5. Memory operations
        int memOps = 0;
        for (auto &BB : F)
            for (auto &I : BB)
                if (isa<LoadInst>(I) || isa<StoreInst>(I)) memOps++;

        // 6. Type graph complexity
        std::set<Type*> typeNodes;
        for (auto &BB : F)
            for (auto &I : BB) {
                collectTypeNodes(I.getType(), typeNodes);
                for (unsigned i = 0; i < I.getNumOperands(); i++)
                    if (I.getOperand(i))
                        collectTypeNodes(I.getOperand(i)->getType(), typeNodes);
            }
        int typeComplexity = (int)typeNodes.size();

        // Emit CSV row to stderr
        errs() << F.getName()    << ","
               << instrCount     << ","
               << bbCount        << ","
               << loopDepth      << ","
               << phiCount       << ","
               << memOps         << ","
               << typeComplexity << "\n";

        return PreservedAnalyses::all();
    }
};

extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "ComplexityPass", "v0.3",
        [](PassBuilder &PB) {
            // Register for explicit -passes="complexity-pass" use
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) -> bool {
                    if (Name == "complexity-pass") {
                        FPM.addPass(ComplexityPass());
                        return true;
                    }
                    return false;
                });

            // Also register so it runs on every function during any pipeline
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel) {
                    FunctionPassManager FPM;
                    FPM.addPass(ComplexityPass());
                    MPM.addPass(createModuleToFunctionPassAdaptor(std::move(FPM)));
                });
        }
    };
}
