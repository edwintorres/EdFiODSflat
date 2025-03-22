## 🧑‍💻 Fixing WSL Always Running as Root

If you're launching WSL and it always dumps you into `root@...`, chances are no non-root user was ever created. This causes issues with tools like Jupyter, SDKMAN, and more.

Here’s how to set up a proper non-root user and make your WSL experience ✨ functional.

---

### ✅ Step 1: Create a Non-Root User

Inside your WSL terminal (running as root), create a new user:

```bash
adduser yourusername
```

Follow the prompts to set a password (you can skip the full name/details).

Then give this new user sudo privileges:

```bash
usermod -aG sudo yourusername
```

---

### ✅ Step 2: Launch WSL as That User

From **PowerShell**, run:

```powershell
wsl -d Ubuntu-22.04 -u yourusername
```

If that drops you into the new user's shell (`yourusername@your-machine`), you're good!

---

### ✅ Step 3: Make It the Default

To make this the default login user for WSL:

```powershell
ubuntu2204 config --default-user yourusername
```

> ⚠️ If `ubuntu2204` doesn't work, try `ubuntu` or check your distro name with:
> ```powershell
> wsl --list --verbose
> ```

You can also use this form:

```powershell
C:\Users\yourname\AppData\Local\Microsoft\WindowsApps\ubuntu2204.exe config --default-user yourusername
```

---

### ✅ Step 4: Confirm It Works

Close WSL, then reopen it:

```powershell
wsl
```

You should now see:

```
yourusername@your-machine:~$
```

No more root-only life. Your tools (like Jupyter) will stop complaining, and your environment will behave as expected. 🎉

---

## 🚫 Avoid Cloning into /mnt/c — Use Native WSL Paths

If you clone your repos into Windows-mounted paths like `/mnt/c/Users/...`, you may hit permission errors like:

```
error: chmod on ... failed
```

This happens because Git inside WSL can't apply Unix permissions on the Windows file system.

### ✅ Do This Instead

Clone your repos into your WSL home directory:

```bash
cd ~
mkdir -p repos
cd repos
git clone https://github.com/yourusername/your-repo.git
```

Your project will now live in `/home/youruser/repos/your-repo`, where WSL has full control.

This avoids permission issues, improves performance, and makes your setup way more stable for things like Git, Spark, and Jupyter.
