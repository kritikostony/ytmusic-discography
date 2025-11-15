{ ... }:
let
  mkHost = import ../lib/mkHost.nix;
in
mkHost {
  hostName = "tony-download-laptop";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
        pkgs.git
        pkgs.vlc
        pkgs.firefox
        pkgs.brave
        pkgs.stremio
        pkgs.qbittorrent
        pkgs.transmission_gtk
        pkgs.aria2
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
    })
  ];
}
