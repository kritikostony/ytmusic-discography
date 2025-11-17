{ config, pkgs, lib, ... }:

let
  mkHost = import ../lib/mkHost.nix;
in
(mkHost {
  hostName = "tony-download-laptop";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
	pkgs.tony-nixos #my custom rebuild command
        pkgs.git
	pkgs.qbittorrent
	pkgs.qbittorrent-cli
	pkgs.protonvpn-gui
	pkgs.protonvpn-cli
	pkgs.firefox
	pkgs.brave
	pkgs.vscode
 	pkgs.stremio
        pkgs.kdePackages.dolphin       # File manager
        pkgs.kdePackages.konsole       # Terminal
        pkgs.kdePackages.kate          # Editor
        pkgs.jetbrains.pycharm-community-bin
      ];

      # Disable KDE bloatware
      environment.plasma6.excludePackages = with pkgs.kdePackages; [
        discover          # AppStore (Flatpak/Snap) – unnecessary on NixOS
        elisa             # Music player
        dragon            # Video player
        kmines            # Games
        kmahjongg         # Games
        okular            # PDF reader (optional)
        kwalletmanager    # If you don't want the wallet UI
      ];

      services.xserver = {
        enable = true;
        displayManager.sddm.enable = true;
        desktopManager.plasma6.enable = true;
      };

      services.transmission = {
        enable = true;
        openRPCPort = true;
      };

      security.chromiumSuidSandbox.enable = true;
      networking.networkmanager.enable = true;
      networking.wireless.enable = false;
      hardware.enableRedistributableFirmware = true;

      boot.loader.grub = {
  	enable = true;
  	device = "/dev/sda";
      };
    })
  ];
}) {
  inherit config pkgs lib;
}
