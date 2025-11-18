{ ... }:
let
  mkHost = import ../lib/mkHost.nix;
in
mkHost {
  hostName = "tony-laptop";
  extraModules = [
    ({ pkgs, lib, ... }: {
      environment.systemPackages = lib.mkAfter [
        pkgs.firefox
        pkgs.vscode
        pkgs.thunderbird
      ];

      services.xserver = {
        enable = true;
        displayManager.sddm.enable = true;
        desktopManager.plasma6.enable = true;
      };

      networking.networkmanager.enable = true;
      hardware.enableRedistributableFirmware = true;
      hardware.bluetooth.enable = true;
      services.printing.enable = true;
    })
  ];
}
