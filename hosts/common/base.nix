{ config, pkgs, lib, ... }:
{
  imports = [ ];

  nix.settings = {
    experimental-features = [ "nix-command" "flakes" ];
    auto-optimise-store = true;
  };

  time.timeZone = lib.mkDefault "Europe/Athens";
  i18n.defaultLocale = lib.mkDefault "en_US.UTF-8";

  console = {
    keyMap = lib.mkDefault "us";
    font = lib.mkDefault "Lat2-Terminus16";
  };

  services.openssh = {
    enable = true;
    settings.PasswordAuthentication = false;
  };

  security.sudo = {
    enable = true;
    wheelNeedsPassword = true;
  };

  networking.firewall.enable = true;

  environment.systemPackages = lib.mkDefault (with pkgs; [
    git
    nano
    vim
    htop
  ]);

  nixpkgs.config.allowUnfree = true;

  system.stateVersion = "25.05";
}
