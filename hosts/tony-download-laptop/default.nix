{ config, pkgs, lib, ... }:

let
  mkHost = import ../lib/mkHost.nix;
in
(mkHost {
  hostName = "tony-download-laptop";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter (with pkgs; [
        tony-nixos                    # custom rebuild command
        git
        qbittorrent
        qbittorrent-cli
        protonvpn-gui
        protonvpn-cli
        firefox
        brave
        vscode
        stremio
        kdePackages.dolphin           # File manager
        kdePackages.konsole           # Terminal
        kdePackages.kate              # Editor
        jetbrains.pycharm-community-bin
      ]);

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

      programs.dconf.enable = true;

      services = {
        xserver = {
          enable = true;
          libinput.enable = true;
          displayManager.sddm = {
            enable = true;
            wayland.enable = true;
          };
          desktopManager.plasma6.enable = true;
        };

        pipewire = {
          enable = true;
          alsa.enable = true;
          alsa.support32Bit = true;
          pulse.enable = true;
        };

        transmission = {
          enable = true;
          openRPCPort = true;
        };
      };

      hardware.graphics = {
        enable = true;
        enable32Bit = true;
      };

      xdg.portal = {
        enable = true;
        xdgOpenUsePortal = true;
        extraPortals = with pkgs; [
          xdg-desktop-portal-kde
          xdg-desktop-portal-gtk
        ];
      };

      environment.sessionVariables = {
        MOZ_ENABLE_WAYLAND = "1";
        NIXOS_OZONE_WL = "1";
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
