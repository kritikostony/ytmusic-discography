{
  # Replace each placeholder value and copy this file to secrets/secret.nix.
  tony-server = {
    rootPasswordHash = "<replace-with-root-password-hash>";
    primaryUser = {
      name = "tony";
      description = "Main server administrator";
      passwordHash = "<replace-with-tony-server-user-password-hash>";
      extraGroups = [ "wheel" "networkmanager" "docker" ];
      authorizedKeys = [
        "ssh-ed25519 AAA...replace-this-with-your-key"
      ];
    };
  };

  "tony-backup-server" = {
    rootPasswordHash = "<replace-with-root-password-hash>";
    primaryUser = {
      name = "tone";
      description = "Backup server administrator";
      passwordHash = "<replace-with-backup-user-password-hash>";
      extraGroups = [ "wheel" "networkmanager" ];
      authorizedKeys = [
        "ssh-ed25519 AAA...replace-this-with-your-key"
      ];
    };
  };

  "tony-laptop" = {
    rootPasswordHash = "<replace-with-root-password-hash>";
    primaryUser = {
      name = "tony";
      description = "Personal laptop user";
      passwordHash = "<replace-with-tony-laptop-user-password-hash>";
      extraGroups = [ "wheel" "networkmanager" "audio" "video" ];
      authorizedKeys = [
        "ssh-ed25519 AAA...replace-this-with-your-key"
      ];
    };
  };

  "tony-download-laptop" = {
    rootPasswordHash = "<replace-with-root-password-hash>";
    primaryUser = {
      name = "download";
      description = "Download workstation user";
      passwordHash = "<replace-with-download-user-password-hash>";
      extraGroups = [ "wheel" "networkmanager" ];
      authorizedKeys = [
        "ssh-ed25519 AAA...replace-this-with-your-key"
      ];
    };
  };
}
