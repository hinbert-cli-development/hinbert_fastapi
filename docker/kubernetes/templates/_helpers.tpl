{{- define "hinbert-fastapi.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- define "hinbert-fastapi.labels" -}}
app.kubernetes.io/name: {{ include "hinbert-fastapi.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
{{- define "hinbert-fastapi.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hinbert-fastapi.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
