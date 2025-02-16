// At the beginning of app.js, add this function:
function loadScript(url, callback) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.onload = function() {
        callback();
    };
    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}

$(document).ready(function() {
    let isRTL = false;

$(document).ready(function() {
 // Wait for the DOM to be fully loaded
 $(window).on('load', function() {
 // Get the current URL
 let currentUrl = new URL(window.location.href);
 
 // Extract the 'file' parameter value
 let fileUrl = currentUrl.searchParams.get('file');

 // Ensure we have a file URL
 if (fileUrl) {
 // Show loading spinner
 $('#loadingSpinner').show();
 $('#resultContainer').hide();

 // Send AJAX request
 $.ajax({
 url: 'process.php',
 type: 'POST',
 data: { fileUrl: fileUrl },
 dataType: 'json',
 success: function(response) {
 $('#loadingSpinner').hide();
 $('#resultContainer').show();
 $('#resultDiv').html(markdownCleanerResult(response.summary));

 // Check if the content contains Persian characters
 isRTL = /[\u0600-\u06FF]/.test(response.summary);
 updateDirection();
 },
 error: function() {
 alert('An error occurred while processing the file.');
 $('#loadingSpinner').hide();
 }
 });
 } else {
 console.error('No file URL provided in the query string.');
 }
 });
});





    $('#downloadDocx').click(function() {
        if (typeof htmlDocx === 'undefined') {
            loadScript("https://cdnjs.cloudflare.com/ajax/libs/html-docx-js/0.3.1/html-docx.min.js", function() {
                convertToDocx();
            });
        } else {
            convertToDocx();
        }
    });




    $('#downloadTxt').click(function() {
        let content = $('#resultDiv').text();
        let blob = new Blob([content], {type: 'text/plain'});
        let link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'summary.txt';
        link.click();
    });

    // Copy Button
    document.getElementById('copyClipboard').addEventListener('click', function () {
        const outputElement = document.getElementById('resultDiv');
        const htmlContent = outputElement.innerHTML;

        // Create a Blob with the HTML content
        const blob = new Blob([htmlContent], { type: 'text/html' });

        // Use the Clipboard API to write the rich text to the clipboard
        navigator.clipboard.write([
            new ClipboardItem({
                'text/html': blob
            })
        ]).then(() => {
           // alert('Content copied to clipboard with formatting!');
        }).catch((err) => {
            console.error('Failed to copy:', err);
            //alert('Failed to copy content to clipboard.');
        });
    });


    $('#toggleDirection').click(function() {
        isRTL = !isRTL;
        updateDirection();
    });

    function updateDirection() {
        $('#resultDiv').css('direction', isRTL ? 'rtl' : 'ltr');
    }
});


    console.log(typeof htmlDocx); // Should print "object" if loaded correctly
// Modify the download button click handler:
$("#downloadDocx").click(function() {
    
    var content = document.getElementById("resultDiv").innerHTML;
    
    
      // Regular expression to check for Persian characters (Unicode range: 0600ā€“06FF)
      var persianRegex = /[\u0600-\u06FF]/;
    
      // Check if the content contains any Persian characters
      var hasPersian = persianRegex.test(content);
      var directionCheck = '';
    
      if (hasPersian) {
        directionCheck = 'rtl';
      } else {
         directionCheck = 'ltr';
      }

    
    
    
    
    
    var fullHtml = `<!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { direction: ${directionCheck}; font-family: iransansx, iransans, iransansfanum, iranyekan, Arial, sans-serif; }
                        </style>
                    </head>
                    <body>${content}</body>
                    </html>`;

    if (typeof htmlDocx === 'undefined') {
        loadScript("https://cdn.jsdelivr.net/npm/html-docx-js@0.3.1/dist/html-docx.min.js", function() {
            convertToDocx(fullHtml);
        });
    } else {
        convertToDocx(fullHtml);
    }
});





function convertToDocx(fullHtml) {
    setTimeout(function() {
        if (typeof htmlDocx !== 'undefined') {
            try {
                var converted = htmlDocx.asBlob(fullHtml);
                var link = document.createElement("a");
                link.href = URL.createObjectURL(converted);
                link.download = "document.docx"; 
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } catch (error) {
                console.error('Error during conversion:', error);
                alert('An error occurred while generating the DOCX file. Please try again.');
            }
        } else {
            console.error('htmlDocx is still not defined after loading. There might be an issue with the library.');
            alert('Unable to generate DOCX. The required library could not be loaded. Please check your internet connection and try again.');
        }
    }, 500);
}

function markdownCleanerResult(data){
    // Retrieve raw HTML content
    var rawHtmlContent = data;

    // Decode HTML entities (including &amp;gt;)
    var decodedMarkdown = rawHtmlContent
        .replace(/&amp;/g, '&')  // Decode &amp;
        .replace(/&gt;/g, '>')   // Decode &gt;
        .replace(/&lt;/g, '<');  // Decode &lt;

    // Convert Markdown syntax to HTML
    var htmlText = decodedMarkdown
        // Headings
        .replace(/^######\s*(.+)/gm, '<h6>$1</h6>')
        .replace(/^#####\s*(.+)/gm, '<h5>$1</h5>')
        .replace(/^####\s*(.+)/gm, '<h4>$1</h4>')
        .replace(/^###\s*(.+)/gm, '<h3>$1</h3>')
        .replace(/^##\s*(.+)/gm, '<h2>$1</h2>')
        .replace(/^#\s*(.+)/gm, '<h1>$1</h1>')
        // Bold and Italic
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.+?)__/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/_(.+?)_/g, '<em>$1</em>')
        // Blockquote (multi-line and nested support)
        .replace(/(^|\n)> ?(.*(?:\n(?!\n)[^>].*)*)/g, function(match, prefix, content) {
            let cleanedContent = content.replace(/^> ?/gm, ''); // Remove leading '>' and optional spaces
            return prefix + '<blockquote>' + cleanedContent + '</blockquote>';
        })
        // Unordered List Items - Add a specific class to differentiate
        .replace(/^\s*[-*]\s+(.+)/gm, '<li class="ul-item">$1</li>')
        // Ordered List Items - Add a specific class to differentiate
        .replace(/^\s*\d+\.\s+(.+)/gm, '<li class="ol-item">$1</li>')
        // Wrap consecutive unordered list items with <ul>
        .replace(/(<li class="ul-item">[^<]+<\/li>)+/g, function(match) {
            return '<ul>' + match + '</ul>';
        })
        // Wrap consecutive ordered list items with <ol>
        .replace(/(<li class="ol-item">[^<]+<\/li>)+/g, function(match) {
            return '<ol>' + match + '</ol>';
        })
        // Inline Code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Horizontal Rule
        .replace(/^\s*(---|\*\*\*)\s*$/gm, '<hr>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
        // Images
        .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img alt="$1" src="$2">')
        // Remove unnecessary nested list tags (optional, based on new implementation)
        .replace(/<\/(ul|ol)>\s*<\1>/g, '');

    // Optional: Remove the specific classes after wrapping if not needed
    htmlText = htmlText
        .replace(/<li class="ul-item">/g, '<li>')
        .replace(/<li class="ol-item">/g, '<li>');

    // Update the div with the converted HTML
    return htmlText;
}
