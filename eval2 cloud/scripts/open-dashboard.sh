#!/usr/bin/env bash
# Open the Kubernetes Dashboard (keep this terminal open while using it).
# The upstream Helm chart repo returned 404 after the project was archived,
# so the Dashboard bundled with minikube is used. No token needed.
exec minikube dashboard
