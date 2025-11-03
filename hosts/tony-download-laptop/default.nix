{ ... }:
let
  mkHost = import ../lib/mkHost.nix;
in
mkHost {
  hostName = "tony-download-laptop";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
        pkgs.qbittorrent
        pkgs.transmission_gtk
        pkgs.aria2
      ];

      services.transmission = {
        enable = true;
        openRPCPort = true;
      };
    })
  ];
}
