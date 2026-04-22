; ModuleID = '/home/adminishitha/llvm-complexity-estimator/training/sample3.c'
source_filename = "/home/adminishitha/llvm-complexity-estimator/training/sample3.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.Vec3 = type { float, float, float }

; Function Attrs: noinline nounwind optnone uwtable
define dso_local float @dot(<2 x float> %0, float %1, <2 x float> %2, float %3) #0 {
  %5 = alloca %struct.Vec3, align 4
  %6 = alloca { <2 x float>, float }, align 4
  %7 = alloca %struct.Vec3, align 4
  %8 = alloca { <2 x float>, float }, align 4
  %9 = getelementptr inbounds { <2 x float>, float }, ptr %6, i32 0, i32 0
  store <2 x float> %0, ptr %9, align 4
  %10 = getelementptr inbounds { <2 x float>, float }, ptr %6, i32 0, i32 1
  store float %1, ptr %10, align 4
  call void @llvm.memcpy.p0.p0.i64(ptr align 4 %5, ptr align 4 %6, i64 12, i1 false)
  %11 = getelementptr inbounds { <2 x float>, float }, ptr %8, i32 0, i32 0
  store <2 x float> %2, ptr %11, align 4
  %12 = getelementptr inbounds { <2 x float>, float }, ptr %8, i32 0, i32 1
  store float %3, ptr %12, align 4
  call void @llvm.memcpy.p0.p0.i64(ptr align 4 %7, ptr align 4 %8, i64 12, i1 false)
  %13 = getelementptr inbounds %struct.Vec3, ptr %5, i32 0, i32 0
  %14 = load float, ptr %13, align 4
  %15 = getelementptr inbounds %struct.Vec3, ptr %7, i32 0, i32 0
  %16 = load float, ptr %15, align 4
  %17 = getelementptr inbounds %struct.Vec3, ptr %5, i32 0, i32 1
  %18 = load float, ptr %17, align 4
  %19 = getelementptr inbounds %struct.Vec3, ptr %7, i32 0, i32 1
  %20 = load float, ptr %19, align 4
  %21 = fmul float %18, %20
  %22 = call float @llvm.fmuladd.f32(float %14, float %16, float %21)
  %23 = getelementptr inbounds %struct.Vec3, ptr %5, i32 0, i32 2
  %24 = load float, ptr %23, align 4
  %25 = getelementptr inbounds %struct.Vec3, ptr %7, i32 0, i32 2
  %26 = load float, ptr %25, align 4
  %27 = call float @llvm.fmuladd.f32(float %24, float %26, float %22)
  ret float %27
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fmuladd.f32(float, float, float) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @normalize(ptr noundef %0) #3 {
  %2 = alloca ptr, align 8
  %3 = alloca float, align 4
  store ptr %0, ptr %2, align 8
  %4 = load ptr, ptr %2, align 8
  %5 = getelementptr inbounds %struct.Vec3, ptr %4, i32 0, i32 0
  %6 = load float, ptr %5, align 4
  %7 = load ptr, ptr %2, align 8
  %8 = getelementptr inbounds %struct.Vec3, ptr %7, i32 0, i32 0
  %9 = load float, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds %struct.Vec3, ptr %10, i32 0, i32 1
  %12 = load float, ptr %11, align 4
  %13 = load ptr, ptr %2, align 8
  %14 = getelementptr inbounds %struct.Vec3, ptr %13, i32 0, i32 1
  %15 = load float, ptr %14, align 4
  %16 = fmul float %12, %15
  %17 = call float @llvm.fmuladd.f32(float %6, float %9, float %16)
  %18 = load ptr, ptr %2, align 8
  %19 = getelementptr inbounds %struct.Vec3, ptr %18, i32 0, i32 2
  %20 = load float, ptr %19, align 4
  %21 = load ptr, ptr %2, align 8
  %22 = getelementptr inbounds %struct.Vec3, ptr %21, i32 0, i32 2
  %23 = load float, ptr %22, align 4
  %24 = call float @llvm.fmuladd.f32(float %20, float %23, float %17)
  store float %24, ptr %3, align 4
  %25 = load float, ptr %3, align 4
  %26 = fcmp ogt float %25, 0.000000e+00
  br i1 %26, label %27, label %45

27:                                               ; preds = %1
  %28 = load float, ptr %3, align 4
  %29 = fdiv float 1.000000e+00, %28
  store float %29, ptr %3, align 4
  %30 = load float, ptr %3, align 4
  %31 = load ptr, ptr %2, align 8
  %32 = getelementptr inbounds %struct.Vec3, ptr %31, i32 0, i32 0
  %33 = load float, ptr %32, align 4
  %34 = fmul float %33, %30
  store float %34, ptr %32, align 4
  %35 = load float, ptr %3, align 4
  %36 = load ptr, ptr %2, align 8
  %37 = getelementptr inbounds %struct.Vec3, ptr %36, i32 0, i32 1
  %38 = load float, ptr %37, align 4
  %39 = fmul float %38, %35
  store float %39, ptr %37, align 4
  %40 = load float, ptr %3, align 4
  %41 = load ptr, ptr %2, align 8
  %42 = getelementptr inbounds %struct.Vec3, ptr %41, i32 0, i32 2
  %43 = load float, ptr %42, align 4
  %44 = fmul float %43, %40
  store float %44, ptr %42, align 4
  br label %45

45:                                               ; preds = %27, %1
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @transformPoints(ptr noundef %0, i32 noundef %1, float noundef %2) #3 {
  %4 = alloca ptr, align 8
  %5 = alloca i32, align 4
  %6 = alloca float, align 4
  %7 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store i32 %1, ptr %5, align 4
  store float %2, ptr %6, align 4
  store i32 0, ptr %7, align 4
  br label %8

8:                                                ; preds = %41, %3
  %9 = load i32, ptr %7, align 4
  %10 = load i32, ptr %5, align 4
  %11 = icmp slt i32 %9, %10
  br i1 %11, label %12, label %44

12:                                               ; preds = %8
  %13 = load float, ptr %6, align 4
  %14 = load ptr, ptr %4, align 8
  %15 = load i32, ptr %7, align 4
  %16 = sext i32 %15 to i64
  %17 = getelementptr inbounds %struct.Vec3, ptr %14, i64 %16
  %18 = getelementptr inbounds %struct.Vec3, ptr %17, i32 0, i32 0
  %19 = load float, ptr %18, align 4
  %20 = fmul float %19, %13
  store float %20, ptr %18, align 4
  %21 = load float, ptr %6, align 4
  %22 = load ptr, ptr %4, align 8
  %23 = load i32, ptr %7, align 4
  %24 = sext i32 %23 to i64
  %25 = getelementptr inbounds %struct.Vec3, ptr %22, i64 %24
  %26 = getelementptr inbounds %struct.Vec3, ptr %25, i32 0, i32 1
  %27 = load float, ptr %26, align 4
  %28 = fmul float %27, %21
  store float %28, ptr %26, align 4
  %29 = load float, ptr %6, align 4
  %30 = load ptr, ptr %4, align 8
  %31 = load i32, ptr %7, align 4
  %32 = sext i32 %31 to i64
  %33 = getelementptr inbounds %struct.Vec3, ptr %30, i64 %32
  %34 = getelementptr inbounds %struct.Vec3, ptr %33, i32 0, i32 2
  %35 = load float, ptr %34, align 4
  %36 = fmul float %35, %29
  store float %36, ptr %34, align 4
  %37 = load ptr, ptr %4, align 8
  %38 = load i32, ptr %7, align 4
  %39 = sext i32 %38 to i64
  %40 = getelementptr inbounds %struct.Vec3, ptr %37, i64 %39
  call void @normalize(ptr noundef %40)
  br label %41

41:                                               ; preds = %12
  %42 = load i32, ptr %7, align 4
  %43 = add nsw i32 %42, 1
  store i32 %43, ptr %7, align 4
  br label %8, !llvm.loop !6

44:                                               ; preds = %8
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @searchMatrix(ptr noundef %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca i32, align 4
  %5 = alloca ptr, align 8
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  store ptr %0, ptr %5, align 8
  store i32 %1, ptr %6, align 4
  store i32 %2, ptr %7, align 4
  store i32 0, ptr %8, align 4
  br label %10

10:                                               ; preds = %39, %3
  %11 = load i32, ptr %8, align 4
  %12 = load i32, ptr %6, align 4
  %13 = icmp slt i32 %11, %12
  br i1 %13, label %14, label %42

14:                                               ; preds = %10
  store i32 0, ptr %9, align 4
  br label %15

15:                                               ; preds = %35, %14
  %16 = load i32, ptr %9, align 4
  %17 = icmp slt i32 %16, 32
  br i1 %17, label %18, label %38

18:                                               ; preds = %15
  %19 = load ptr, ptr %5, align 8
  %20 = load i32, ptr %8, align 4
  %21 = sext i32 %20 to i64
  %22 = getelementptr inbounds [32 x i32], ptr %19, i64 %21
  %23 = load i32, ptr %9, align 4
  %24 = sext i32 %23 to i64
  %25 = getelementptr inbounds [32 x i32], ptr %22, i64 0, i64 %24
  %26 = load i32, ptr %25, align 4
  %27 = load i32, ptr %7, align 4
  %28 = icmp eq i32 %26, %27
  br i1 %28, label %29, label %34

29:                                               ; preds = %18
  %30 = load i32, ptr %8, align 4
  %31 = mul nsw i32 %30, 32
  %32 = load i32, ptr %9, align 4
  %33 = add nsw i32 %31, %32
  store i32 %33, ptr %4, align 4
  br label %43

34:                                               ; preds = %18
  br label %35

35:                                               ; preds = %34
  %36 = load i32, ptr %9, align 4
  %37 = add nsw i32 %36, 1
  store i32 %37, ptr %9, align 4
  br label %15, !llvm.loop !8

38:                                               ; preds = %15
  br label %39

39:                                               ; preds = %38
  %40 = load i32, ptr %8, align 4
  %41 = add nsw i32 %40, 1
  store i32 %41, ptr %8, align 4
  br label %10, !llvm.loop !9

42:                                               ; preds = %10
  store i32 -1, ptr %4, align 4
  br label %43

43:                                               ; preds = %42, %29
  %44 = load i32, ptr %4, align 4
  ret i32 %44
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="64" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
!9 = distinct !{!9, !7}
