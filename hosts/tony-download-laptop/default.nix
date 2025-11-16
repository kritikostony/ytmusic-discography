{ config, pkgs, lib, ... }:

let
  mkHost = import ../lib/mkHost.nix;
in
(mkHost {
  hostName = "tony-download-laptop";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
        pkgs.git
	pkgs.qbittorrent
      ];

      services.xserver = {
        enable = true;
        displayManager.gdm.enable = true;
        desktopManager.gnome.enable = true;
      };

      services.transmission = {
        enable = true;
        openRPCPort = true;
      };

      boot.loader.grub = {
  	enable = true;
  	device = "/dev/sda";
      };
    })
  ];
}) {
  inherit config pkgs lib;
}
