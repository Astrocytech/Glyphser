# Release Checksum Signing

Use these commands to publish a detached signature for the checksum file.

## Create Signature
```bash
gpg --armor --detach-sign --output docs/release/CHECKSUMS_v0.1.0.sha256.asc docs/release/CHECKSUMS_v0.1.0.sha256
```

## Verify Signature
```bash
gpg --verify docs/release/CHECKSUMS_v0.1.0.sha256.asc docs/release/CHECKSUMS_v0.1.0.sha256
```

## Public Verification Flow
- Publish `docs/release/CHECKSUMS_v0.1.0.sha256`.
- Publish `docs/release/CHECKSUMS_v0.1.0.sha256.asc`.
- Publish your public key fingerprint in release notes or project profile.
