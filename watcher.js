const chokidar = require('chokidar');
const fs = require('fs');
const path = require('path');

const baseTemplatePath = path.join(__dirname, 'assets/dynamic-video-template/base_template.html');
const updatedTemplatePath = path.join(__dirname, 'assets/dynamic-video-template/updated_template.html');

// Initialize the watcher
const watcher = chokidar.watch(baseTemplatePath, {
  persistent: true
});

// Event listener for file change
watcher.on('change', (filePath) => {
  console.log(`File ${filePath} has been changed. Copying contents to updated_template.html...`);
  
  // Read the base template
  fs.readFile(baseTemplatePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading base template:', err);
      return;
    }

    // Write to the updated template
    fs.writeFile(updatedTemplatePath, data, 'utf8', (err) => {
      if (err) {
        console.error('Error writing to updated template:', err);
        return;
      }
      console.log('Contents copied to updated_template.html successfully.');
    });
  });
});

console.log('Watching for changes in base_template.html...'); 