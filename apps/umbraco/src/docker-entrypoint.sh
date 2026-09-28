#!/bin/sh
set -eu

cert_dir="${UMBRACO_CERT_DIR:-/app/umbraco/certs}"
cert_path="${UMBRACO_CERT_PATH:-${cert_dir}/umbraco-selfsigned.pfx}"
host_file="${cert_dir}/.hostname"
host_raw="${W9_URL:-localhost}"
host_name="${host_raw%%:*}"
cert_password="${ASPNETCORE_Kestrel__Certificates__Default__Password:-${UMBRACO_HTTPS_CERT_PASSWORD:-umbraco-selfsigned}}"

mkdir -p "${cert_dir}"

needs_regen=0
if [ ! -f "${cert_path}" ]; then
  needs_regen=1
fi
if [ ! -f "${host_file}" ] || [ "$(cat "${host_file}" 2>/dev/null || true)" != "${host_name}" ]; then
  needs_regen=1
fi

if [ "${needs_regen}" -eq 1 ]; then
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir}"' EXIT

  san_entries="DNS:localhost,IP:127.0.0.1"
  if printf '%s' "${host_name}" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
    san_entries="${san_entries},IP:${host_name}"
  else
    san_entries="${san_entries},DNS:${host_name}"
  fi

  cat > "${tmpdir}/openssl.cnf" <<EOF
[req]
distinguished_name = dn
x509_extensions = req_ext
prompt = no

[dn]
CN = ${host_name}

[req_ext]
subjectAltName = ${san_entries}
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
EOF

  echo "Generating self-signed HTTPS certificate for ${host_name}"
  openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 825 \
    -keyout "${tmpdir}/key.pem" \
    -out "${tmpdir}/cert.pem" \
    -config "${tmpdir}/openssl.cnf" >/dev/null 2>&1

  openssl pkcs12 -export \
    -out "${cert_path}" \
    -inkey "${tmpdir}/key.pem" \
    -in "${tmpdir}/cert.pem" \
    -passout pass:"${cert_password}" >/dev/null 2>&1

  printf '%s' "${host_name}" > "${host_file}"
  trap - EXIT
  rm -rf "${tmpdir}"
fi

exec dotnet UmbracoApp.dll
