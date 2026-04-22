; ModuleID = '/home/adminishitha/llvm-complexity-estimator/training/sample5.c'
source_filename = "/home/adminishitha/llvm-complexity-estimator/training/sample5.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @deepNest(ptr noundef %0, i32 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  store ptr %0, ptr %3, align 8
  store i32 %1, ptr %4, align 4
  store i32 0, ptr %5, align 4
  br label %8

8:                                                ; preds = %45, %2
  %9 = load i32, ptr %5, align 4
  %10 = icmp slt i32 %9, 4
  br i1 %10, label %11, label %48

11:                                               ; preds = %8
  store i32 0, ptr %6, align 4
  br label %12

12:                                               ; preds = %41, %11
  %13 = load i32, ptr %6, align 4
  %14 = icmp slt i32 %13, 4
  br i1 %14, label %15, label %44

15:                                               ; preds = %12
  store i32 0, ptr %7, align 4
  br label %16

16:                                               ; preds = %37, %15
  %17 = load i32, ptr %7, align 4
  %18 = icmp slt i32 %17, 4
  br i1 %18, label %19, label %40

19:                                               ; preds = %16
  %20 = load i32, ptr %4, align 4
  %21 = load i32, ptr %5, align 4
  %22 = add nsw i32 %20, %21
  %23 = load i32, ptr %6, align 4
  %24 = add nsw i32 %22, %23
  %25 = load i32, ptr %7, align 4
  %26 = add nsw i32 %24, %25
  %27 = load ptr, ptr %3, align 8
  %28 = load i32, ptr %5, align 4
  %29 = sext i32 %28 to i64
  %30 = getelementptr inbounds [4 x [4 x i32]], ptr %27, i64 %29
  %31 = load i32, ptr %6, align 4
  %32 = sext i32 %31 to i64
  %33 = getelementptr inbounds [4 x [4 x i32]], ptr %30, i64 0, i64 %32
  %34 = load i32, ptr %7, align 4
  %35 = sext i32 %34 to i64
  %36 = getelementptr inbounds [4 x i32], ptr %33, i64 0, i64 %35
  store i32 %26, ptr %36, align 4
  br label %37

37:                                               ; preds = %19
  %38 = load i32, ptr %7, align 4
  %39 = add nsw i32 %38, 1
  store i32 %39, ptr %7, align 4
  br label %16, !llvm.loop !6

40:                                               ; preds = %16
  br label %41

41:                                               ; preds = %40
  %42 = load i32, ptr %6, align 4
  %43 = add nsw i32 %42, 1
  store i32 %43, ptr %6, align 4
  br label %12, !llvm.loop !8

44:                                               ; preds = %12
  br label %45

45:                                               ; preds = %44
  %46 = load i32, ptr %5, align 4
  %47 = add nsw i32 %46, 1
  store i32 %47, ptr %5, align 4
  br label %8, !llvm.loop !9

48:                                               ; preds = %8
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @tensorOp(ptr noundef %0, ptr noundef %1, ptr noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %10

10:                                               ; preds = %63, %3
  %11 = load i32, ptr %7, align 4
  %12 = icmp slt i32 %11, 8
  br i1 %12, label %13, label %66

13:                                               ; preds = %10
  store i32 0, ptr %8, align 4
  br label %14

14:                                               ; preds = %59, %13
  %15 = load i32, ptr %8, align 4
  %16 = icmp slt i32 %15, 8
  br i1 %16, label %17, label %62

17:                                               ; preds = %14
  store i32 0, ptr %9, align 4
  br label %18

18:                                               ; preds = %55, %17
  %19 = load i32, ptr %9, align 4
  %20 = icmp slt i32 %19, 8
  br i1 %20, label %21, label %58

21:                                               ; preds = %18
  %22 = load ptr, ptr %4, align 8
  %23 = load i32, ptr %7, align 4
  %24 = sext i32 %23 to i64
  %25 = getelementptr inbounds [8 x [8 x float]], ptr %22, i64 %24
  %26 = load i32, ptr %8, align 4
  %27 = sext i32 %26 to i64
  %28 = getelementptr inbounds [8 x [8 x float]], ptr %25, i64 0, i64 %27
  %29 = load i32, ptr %9, align 4
  %30 = sext i32 %29 to i64
  %31 = getelementptr inbounds [8 x float], ptr %28, i64 0, i64 %30
  %32 = load float, ptr %31, align 4
  %33 = load ptr, ptr %5, align 8
  %34 = load i32, ptr %7, align 4
  %35 = sext i32 %34 to i64
  %36 = getelementptr inbounds [8 x [8 x float]], ptr %33, i64 %35
  %37 = load i32, ptr %8, align 4
  %38 = sext i32 %37 to i64
  %39 = getelementptr inbounds [8 x [8 x float]], ptr %36, i64 0, i64 %38
  %40 = load i32, ptr %9, align 4
  %41 = sext i32 %40 to i64
  %42 = getelementptr inbounds [8 x float], ptr %39, i64 0, i64 %41
  %43 = load float, ptr %42, align 4
  %44 = fmul float %32, %43
  %45 = load ptr, ptr %6, align 8
  %46 = load i32, ptr %7, align 4
  %47 = sext i32 %46 to i64
  %48 = getelementptr inbounds [8 x [8 x float]], ptr %45, i64 %47
  %49 = load i32, ptr %8, align 4
  %50 = sext i32 %49 to i64
  %51 = getelementptr inbounds [8 x [8 x float]], ptr %48, i64 0, i64 %50
  %52 = load i32, ptr %9, align 4
  %53 = sext i32 %52 to i64
  %54 = getelementptr inbounds [8 x float], ptr %51, i64 0, i64 %53
  store float %44, ptr %54, align 4
  br label %55

55:                                               ; preds = %21
  %56 = load i32, ptr %9, align 4
  %57 = add nsw i32 %56, 1
  store i32 %57, ptr %9, align 4
  br label %18, !llvm.loop !10

58:                                               ; preds = %18
  br label %59

59:                                               ; preds = %58
  %60 = load i32, ptr %8, align 4
  %61 = add nsw i32 %60, 1
  store i32 %61, ptr %8, align 4
  br label %14, !llvm.loop !11

62:                                               ; preds = %14
  br label %63

63:                                               ; preds = %62
  %64 = load i32, ptr %7, align 4
  %65 = add nsw i32 %64, 1
  store i32 %65, ptr %7, align 4
  br label %10, !llvm.loop !12

66:                                               ; preds = %10
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @maxIn3D(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  store ptr %0, ptr %2, align 8
  %7 = load ptr, ptr %2, align 8
  %8 = getelementptr inbounds [4 x [4 x i32]], ptr %7, i64 0
  %9 = getelementptr inbounds [4 x [4 x i32]], ptr %8, i64 0, i64 0
  %10 = getelementptr inbounds [4 x i32], ptr %9, i64 0, i64 0
  %11 = load i32, ptr %10, align 4
  store i32 %11, ptr %3, align 4
  store i32 0, ptr %4, align 4
  br label %12

12:                                               ; preds = %58, %1
  %13 = load i32, ptr %4, align 4
  %14 = icmp slt i32 %13, 4
  br i1 %14, label %15, label %61

15:                                               ; preds = %12
  store i32 0, ptr %5, align 4
  br label %16

16:                                               ; preds = %54, %15
  %17 = load i32, ptr %5, align 4
  %18 = icmp slt i32 %17, 4
  br i1 %18, label %19, label %57

19:                                               ; preds = %16
  store i32 0, ptr %6, align 4
  br label %20

20:                                               ; preds = %50, %19
  %21 = load i32, ptr %6, align 4
  %22 = icmp slt i32 %21, 4
  br i1 %22, label %23, label %53

23:                                               ; preds = %20
  %24 = load ptr, ptr %2, align 8
  %25 = load i32, ptr %4, align 4
  %26 = sext i32 %25 to i64
  %27 = getelementptr inbounds [4 x [4 x i32]], ptr %24, i64 %26
  %28 = load i32, ptr %5, align 4
  %29 = sext i32 %28 to i64
  %30 = getelementptr inbounds [4 x [4 x i32]], ptr %27, i64 0, i64 %29
  %31 = load i32, ptr %6, align 4
  %32 = sext i32 %31 to i64
  %33 = getelementptr inbounds [4 x i32], ptr %30, i64 0, i64 %32
  %34 = load i32, ptr %33, align 4
  %35 = load i32, ptr %3, align 4
  %36 = icmp sgt i32 %34, %35
  br i1 %36, label %37, label %49

37:                                               ; preds = %23
  %38 = load ptr, ptr %2, align 8
  %39 = load i32, ptr %4, align 4
  %40 = sext i32 %39 to i64
  %41 = getelementptr inbounds [4 x [4 x i32]], ptr %38, i64 %40
  %42 = load i32, ptr %5, align 4
  %43 = sext i32 %42 to i64
  %44 = getelementptr inbounds [4 x [4 x i32]], ptr %41, i64 0, i64 %43
  %45 = load i32, ptr %6, align 4
  %46 = sext i32 %45 to i64
  %47 = getelementptr inbounds [4 x i32], ptr %44, i64 0, i64 %46
  %48 = load i32, ptr %47, align 4
  store i32 %48, ptr %3, align 4
  br label %49

49:                                               ; preds = %37, %23
  br label %50

50:                                               ; preds = %49
  %51 = load i32, ptr %6, align 4
  %52 = add nsw i32 %51, 1
  store i32 %52, ptr %6, align 4
  br label %20, !llvm.loop !13

53:                                               ; preds = %20
  br label %54

54:                                               ; preds = %53
  %55 = load i32, ptr %5, align 4
  %56 = add nsw i32 %55, 1
  store i32 %56, ptr %5, align 4
  br label %16, !llvm.loop !14

57:                                               ; preds = %16
  br label %58

58:                                               ; preds = %57
  %59 = load i32, ptr %4, align 4
  %60 = add nsw i32 %59, 1
  store i32 %60, ptr %4, align 4
  br label %12, !llvm.loop !15

61:                                               ; preds = %12
  %62 = load i32, ptr %3, align 4
  ret i32 %62
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

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
!10 = distinct !{!10, !7}
!11 = distinct !{!11, !7}
!12 = distinct !{!12, !7}
!13 = distinct !{!13, !7}
!14 = distinct !{!14, !7}
!15 = distinct !{!15, !7}
