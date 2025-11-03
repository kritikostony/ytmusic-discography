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

      hardware.bluetooth.enable = true;
      services.printing.enable = true;
    })
  ];
}
