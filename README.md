# Tony's NixOS configurations

This repository hosts the shared configuration for the different NixOS machines in the homelab:

- `tony-server`: primary server for self-hosted services and data.
- `tony-backup-server`: off-site backup server that wakes up periodically.
- `tony-laptop`: personal workstation.
- `tony-download-laptop`: dedicated download laptop.

## Repository layout

```
.
├── flake.nix
├── hosts/
│   ├── common/              # shared modules imported by every machine
│   ├── lib/                 # helpers (secret loading, host wrapper)
│   ├── tony-server/
│   ├── tony-backup-server/
│   ├── tony-laptop/
│   └── tony-download-laptop/
├── secrets/
│   └── secret_default.nix   # template for machine secrets
└── README.md
```

Each host directory exposes a `default.nix` module that pulls in shared logic from `hosts/lib/mkHost.nix`. The flake outputs are already configured, so you can build or switch a machine with commands like:

```bash
nix build .#tony-server
sudo nixos-rebuild switch --flake .#tony-laptop
```

## Hardware configuration

Hardware configuration files are expected to live **outside** this repository in a sibling directory named `nixos`. For example, the `tony-server` machine imports:

```
../nixos/tony-server/hardware-configuration.nix
```

Make sure that the directory structure looks like this on disk before building:

```
parent-directory/
├── nixos-config/      # this Git repository
└── nixos/
    ├── tony-server/
    │   └── hardware-configuration.nix
    ├── tony-backup-server/
    │   └── hardware-configuration.nix
    ├── tony-laptop/
    │   └── hardware-configuration.nix
    └── tony-download-laptop/
        └── hardware-configuration.nix
```

If a hardware file is missing the build will emit a warning so you know which path to populate.

## Managing secrets

All usernames, password hashes, and SSH keys are loaded from `secrets/secret.nix`. This file is ignored by Git (see `.gitignore`). A template is provided in `secrets/secret_default.nix` – copy it to `secrets/secret.nix` and replace every placeholder with your real values:

```bash
cp secrets/secret_default.nix secrets/secret.nix
$EDITOR secrets/secret.nix
```

Every host entry must define:

- `rootPasswordHash`: the hashed password for the root user.
- `primaryUser`: attributes for the main user on that machine. At minimum supply `name` and `passwordHash`; optional fields include `description`, `extraGroups`, and `authorizedKeys`.

The `users.mutableUsers` option is disabled to ensure that user accounts stay in sync with the values provided by the secrets file.

## Adding new machines

To add another host:

1. Create `secrets/secret.nix` entries for the new hostname.
2. Add a new directory under `hosts/` with a `default.nix` that calls `hosts/lib/mkHost.nix`.
3. Create `../nixos/<hostname>/hardware-configuration.nix` next to this repository.
4. Register the host in `flake.nix` under `nixosConfigurations`.

With that in place the machine can be built with `nix build .#<hostname>` or switched with `sudo nixos-rebuild switch --flake .#<hostname>` on the target system.

## Committing and pushing to GitHub

Once you have the repository set up locally, commit and publish changes with standard Git commands:

```bash
git add .
git commit -m "Describe what you changed"
git branch -M main              # optional, only if you want the branch named main
git remote add origin git@github.com:<username>/<repo>.git
git push -u origin main
```

If the remote already exists, skip the `git remote add` line and just run `git push` (or `git push origin <branch>`). Subsequent updates only need `git add`, `git commit`, and `git push`.
