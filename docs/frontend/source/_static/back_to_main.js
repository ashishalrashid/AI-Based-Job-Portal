// Add Back to Main Menu button to all documentation pages
(function() {
  'use strict';
  
  // Wait for DOM to be ready
  function init() {
    // Calculate the correct path to main index
    const path = window.location.pathname;
    let mainIndexPath = '../../index.html';
    
    // If we're in backend or frontend directory, go up two levels
    if (path.includes('/backend/') || path.includes('/frontend/')) {
      // Count how many levels deep we are
      const depth = (path.match(/\//g) || []).length;
      if (depth > 2) {
        // We're in a subdirectory, go up to main index
        mainIndexPath = '../../index.html';
      } else {
        // We're at the root of backend/frontend, go up one level
        mainIndexPath = '../index.html';
      }
    }
    
    // Create the button
    const button = document.createElement('a');
    button.href = mainIndexPath;
    button.className = 'back-to-main';
    button.textContent = 'Main Menu';
    button.title = 'Return to Documentation Main Menu';
    
    // Add to body
    document.body.appendChild(button);
    
    // Ensure it's visible
    button.style.display = 'inline-flex';
  }
  
  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

