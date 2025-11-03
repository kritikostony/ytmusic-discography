{ ... }:
let
  mkHost = import ../lib/mkHost.nix;
in
mkHost {
  hostName = "tony-backup-server";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
        pkgs.rsync
        pkgs.restic
        pkgs.borgbackup
      ];

      services.openssh.settings = {
        PermitRootLogin = "no";
      };
    })
  ];
}
