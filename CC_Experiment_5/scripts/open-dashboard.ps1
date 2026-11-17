<#
.SYNOPSIS
  Open the Kubernetes Dashboard in the browser (keep this window open while using it).
.NOTES
  The upstream Helm chart repo (https://kubernetes.github.io/dashboard/) returned 404 after the
  project was archived, so the Dashboard bundled with minikube is used instead. No token is needed.
#>
minikube dashboard
