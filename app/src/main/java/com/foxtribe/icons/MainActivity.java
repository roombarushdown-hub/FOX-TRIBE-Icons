package com.foxtribe.icons;
import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.view.Gravity;
public class MainActivity extends Activity {
  @Override public void onCreate(Bundle b) {super.onCreate(b);
    TextView t=new TextView(this); t.setText("FOX TRIBE — Style A\n110 icons\nApply through your launcher's icon-pack settings.\n\nAutomatic app mappings still require verification.");
    t.setTextSize(19); t.setTextColor(0xffefded0); t.setBackgroundColor(0xff171416); t.setPadding(32,32,32,32);t.setGravity(Gravity.CENTER);
    setContentView(t);
  }
}
