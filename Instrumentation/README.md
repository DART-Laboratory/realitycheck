# Instrumentation via Soot

## Note
- Please perform instrumentation only for applications not written in OpenXR API (applications not downloaded directly from Meta Quest 2 store).
- The instrumentation strategy is highlighted in `Section 5.1` and `Appendix E` of the paper.

## Soot Setup
- To run the instrumentation code, you first need to set up Soot on your computer. Soot can run on both Windows and MacOS.
- Detailed instructions on how to set up soot are provided here.
- In addition, you need to install the following version of java. Soot doesn't seem to support versions after this (requires Java version below 9, e.g., 8.):
    * java version "1.8.0_341"
    * Java(TM) SE Runtime Environment (build 1.8.0_341-b10)

## How to instrument:
1. After setting Soot up, please make sure that you set the ANDROID_HOME environmental variable, e.g., export ANDROID_HOME=~/Library/Android/sdk/platforms for osx.
2. In the directory `Demo / Android`, please put the desired `.apk` app that you want to instrument.
3. Sign and run the instrumentation code:
    - run AndroidLogger via CLI by running `./gradlew run --args="AndroidLogger"`
    - It should create demo/Android/Instrumented/<appname>.apk
    - Now, you can sign and install it by running the following commands:
        1. `cd ./demo/Android`
        2. `./sign.sh Instrumented/<appname>.apk key "android"
4. To install the app on your Meta Quest 2 headset, connect it to your PC via USB or TCP and run the following command:
    - `adb install -r -t Instrumented/<appname>.apk`
5. This should automatically leave logs in the system log buffer. You can now proceed to the next step in the main README file.