#!/bin/sh
set -eu

STATE_DIR=/tmp/airbyte-installer
KUBECONFIG_SOURCE=${KUBECONFIG_SOURCE:-/shared/kubeconfig.yaml}
KUBECONFIG_FILE=${STATE_DIR}/kubeconfig.yaml
RUNTIME_HOST=${KUBECONFIG_RUNTIME_HOST:-airbyte}
TIMEOUT=${AIRBYTE_BOOTSTRAP_TIMEOUT:-1800}

mkdir -p "${STATE_DIR}"

ensure_tools() {
  apk add --no-cache bash curl kubectl >/dev/null
}

prepare_kubeconfig() {
  end=$(( $(date +%s) + TIMEOUT ))
  while [ ! -s "${KUBECONFIG_SOURCE}" ]; do
    if [ "$(date +%s)" -ge "${end}" ]; then
      echo "timed out waiting for kubeconfig" >&2
      exit 1
    fi
    sleep 2
  done
  sed "s#https://127.0.0.1:6443#https://${RUNTIME_HOST}:6443#g" "${KUBECONFIG_SOURCE}" > "${KUBECONFIG_FILE}"
  export KUBECONFIG="${KUBECONFIG_FILE}"
}

wait_for_cluster() {
  end=$(( $(date +%s) + TIMEOUT ))
  until kubectl get nodes >/dev/null 2>&1; do
    if [ "$(date +%s)" -ge "${end}" ]; then
      echo "timed out waiting for k3s API" >&2
      exit 1
    fi
    sleep 5
  done
}

render_values() {
  cat > "${STATE_DIR}/airbyte-values.yaml" <<EOF
global:
  edition: community
  airbyteUrl: ${AIRBYTE_PUBLIC_URL}
  auth:
    enabled: true
    instanceAdmin:
      password: ${AIRBYTE_INITIAL_PASSWORD}
    security:
      cookieSecureSetting: "false"
server:
  service:
    type: NodePort
    port: 8001
    nodePort: ${AIRBYTE_NODE_PORT}
EOF
}

install_airbyte() {
  helm repo add airbyte-v2 "${AIRBYTE_HELM_REPO}" >/dev/null 2>&1 || true
  helm repo update airbyte-v2 >/dev/null
  render_values
  helm upgrade --install "${AIRBYTE_HELM_RELEASE}" airbyte-v2/airbyte \
    --namespace "${AIRBYTE_HELM_NAMESPACE}" \
    --create-namespace \
    --version "${W9_VERSION}" \
    -f "${STATE_DIR}/airbyte-values.yaml"
}

wait_for_airbyte() {
  kubectl rollout status deployment/airbyte-server -n "${AIRBYTE_HELM_NAMESPACE}" --timeout="${TIMEOUT}s"
  end=$(( $(date +%s) + TIMEOUT ))
  until curl -fsS "http://${RUNTIME_HOST}:${AIRBYTE_NODE_PORT}/api/v1/health" | grep -q '"available":true'; do
    if [ "$(date +%s)" -ge "${end}" ]; then
      echo "timed out waiting for Airbyte health" >&2
      exit 1
    fi
    sleep 10
  done
}

ensure_tools
prepare_kubeconfig
wait_for_cluster
install_airbyte
wait_for_airbyte
