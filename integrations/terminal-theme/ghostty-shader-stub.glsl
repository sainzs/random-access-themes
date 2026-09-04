#version 430 core
layout(binding = 0) uniform sampler2D iChannel0;
layout(binding = 1) uniform Globals {
  vec3 iResolution; float iTime; float iTimeDelta; float iFrameRate; int iFrame;
  vec4 iMouse; vec4 iDate; float iSampleRate;
  vec4 iCurrentCursor; vec4 iPreviousCursor; vec4 iCurrentCursorColor; vec4 iPreviousCursorColor;
  vec4 iCurrentCursorStyle; vec4 iPreviousCursorStyle; vec4 iCursorVisible;
  float iTimeCursorChange; float iTimeFocus; int iFocus;
  vec3 iBackgroundColor; vec3 iForegroundColor; vec3 iCursorColor; vec3 iCursorText;
  vec3 iSelectionBackgroundColor; vec3 iSelectionForegroundColor;
};
layout(location = 0) out vec4 _fragColor;
