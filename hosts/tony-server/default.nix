{ lib, ... }:
let
  mkHost = import ../lib/mkHost.nix;
in
mkHost {
  hostName = "tony-server";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
        pkgs.curl
        pkgs.wget
        pkgs.jq
        pkgs.lsof
      ];

      services.fail2ban.enable = true;
      services.openssh.settings.X11Forwarding = false;
    })
  ];
}
