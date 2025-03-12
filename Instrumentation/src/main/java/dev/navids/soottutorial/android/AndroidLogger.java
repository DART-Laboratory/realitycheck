package dev.navids.soottutorial.android;
import java.util.Iterator;
import java.util.Map;

import soot.*;
import soot.jimple.*;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;


public class AndroidLogger {

    private final static String USER_HOME = System.getProperty("user.home");
    private static String androidJar = USER_HOME + "/Library/Android/sdk/platforms";
    static String androidDemoPath = System.getProperty("user.dir") + File.separator + "demo" + File.separator + "Android";
    static String apkPath = androidDemoPath + File.separator + "/calc.apk";
    static String outputPath = androidDemoPath + File.separator + "/Instrumented";

    public static void main(String[] args){

        if(System.getenv().containsKey("ANDROID_HOME"))
            androidJar = System.getenv("ANDROID_HOME")+ File.separator+"platforms";
        // Clean the outputPath
        final File[] files = (new File(outputPath)).listFiles();
        if (files != null && files.length > 0) {
            Arrays.asList(files).forEach(File::delete);
        }
        // Initialize Soot
        InstrumentUtil.setupSoot(androidJar, apkPath, outputPath);
        // Add a transformation pack in order to add the statement "System.out.println(<content>) at the beginning of each Application method
        PackManager.v().getPack("jtp").add(new Transform("jtp.myLogger", new BodyTransformer() {
            @Override
            protected void internalTransform(Body b, String phaseName, Map<String, String> options) {
                // First we filter out Android framework methods
                if(AndroidUtil.isAndroidMethod(b.getMethod()))
                    return;
                JimpleBody body1 = (JimpleBody) b;
                UnitPatchingChain units = b.getUnits();
                JimpleBody body2 = (JimpleBody) b;
                final PatchingChain<Unit> itertariveunits = b.getUnits();
                List<Unit> generatedUnits = new ArrayList<>();
                
                for(Iterator<Unit> iter = itertariveunits.snapshotIterator(); iter.hasNext();) {
					final Unit u = iter.next();
                    u.apply(new AbstractStmtSwitch() {
                            public void caseInvokeStmt(InvokeStmt stmt) {
                                InvokeExpr invokeExpr = stmt.getInvokeExpr();
                                String method = invokeExpr.getMethod().getName();

                                if(!method.equals("onPause") && !method.equals("onResume")) {
                                    return;
                                }

                                final List<Value> args = invokeExpr.getArgs();
                                
                                String arguments = args.toString();
                                String content = String.format("%s Beginning of method %s with arguments %s", InstrumentUtil.TAG, method, arguments);

                                Local psLocal = InstrumentUtil.generateNewLocal(body2, RefType.v("java.io.PrintStream"));
                                SootField sysOutField = Scene.v().getField("<java.lang.System: java.io.PrintStream out>");
                                AssignStmt sysOutAssignStmt = Jimple.v().newAssignStmt(psLocal, Jimple.v().newStaticFieldRef(sysOutField.makeRef()));
                                generatedUnits.add(sysOutAssignStmt);

                                SootMethod printlnMethod = Scene.v().grabMethod("<java.io.PrintStream: void println(java.lang.String)>");
                                Value printlnParamter = StringConstant.v(content);
                                InvokeStmt printlnMethodCallStmt = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(psLocal, printlnMethod.makeRef(), printlnParamter));
                                generatedUnits.add(printlnMethodCallStmt);                          
                            }
                    });
                }

                units.insertAfter(generatedUnits, body1.getFirstNonIdentityStmt());         
                b.validate();
            }
        }));
        // Run Soot packs (note that our transformer pack is added to the phase "jtp")
        PackManager.v().runPacks();
        // Write the result of packs in outputPath
        PackManager.v().writeOutput();
    }
    
}