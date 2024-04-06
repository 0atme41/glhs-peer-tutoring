# Connecting to the Server
This will explain exactly how to SSH into the Lightsail instance for VS Code and GitHub Codespaces users. The commands are the same if you use another text editor, as long as you're using Bash.

1. At the top right of the terminal, there should be a plus symbol with a dropdown attached.
   * Click the dropdown
   * Click **Split Terminal**
   * Click **Bash**
   * There should now be two Bash terminals side by side. If the original terminal wasn't bash, delete it and repeat step 1.
2. One terminal will be the local terminal, the other will be connected to the instance. Since I prefer local on the left and instance on the right, I'll be typing these next commands on the right. If you want it on the left, follow these instructions on the left terminal.
   * Enter this command into the right terminal:
```
ssh ubuntu@3.223.69.192 -i key.pem
```
   * You should now be connected to ubuntu@csgator.
   * If this is your first time connecting, you'll probably have to accept a few things as you connect.
   * Enter this command to move into the CSGator folder:
```
ls csgator
```
# Updating the Website
Again, this assumes you're using VS Code or GitHub Codespaces, with the split terminal that was set up in the **Connecting to the Server** section of this README. Furthermore, you should be in the CSGator folder in the instance terminal. This should still translate to other text editors.

1. Once you've made your changes locally, use these commands to push them to GitHub in your local terminal:
```
git add .
git commit -m "ADD A SHORT MESSAGE DESCRIBING YOUR CHANGES HERE"
git push
```
2. Now that the changes have been pushed, use this command to pull them from GitHub in your instance terminal:
```
git pull
```
3. The files are now fully updated in the instance, but the website must be reloaded for the changes to take effect:
```
sudo systemctl restart csgator
```
# Something Didn't Work?
Email me.
```
sjfishburn@students.wcpss.net
```
Or find me in person.
