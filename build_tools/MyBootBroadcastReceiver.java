package org.whitemirror.witnessangeldemo;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import org.whitemirror.witnessangeldemo.ServiceRecordingservice;

public class MyBootBroadcastReceiver extends BroadcastReceiver {
    public void onReceive(Context context, Intent intent) {
        System.err.println("\n\n INSIDE MyBootBroadcastReceiver \n\n");
        String package_root = context.getFilesDir().getAbsolutePath();
        String app_root =  package_root + "/app";
        Intent ix = new Intent(context, ServiceRecordingservice.class);
        ix.putExtra("androidPrivate", package_root);
        ix.putExtra("androidArgument", app_root);
        ix.putExtra("serviceTitle", "Witness Angel Demo");
        ix.putExtra("serviceDescription", "Recordingservice");
        ix.putExtra("serviceEntrypoint", "service.py");
        ix.putExtra("pythonName", "recordingservice");
        ix.putExtra("serviceStartAsForeground", "false");
        ix.putExtra("pythonHome", app_root);
        ix.putExtra("pythonPath", app_root + ":" + app_root + "/lib");
        ix.putExtra("pythonServiceArgument", "");
        ix.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        context.startForegroundService(ix);
        System.err.println("\n\n LEAVING MyBootBroadcastReceiver \n\n");
    }
}
