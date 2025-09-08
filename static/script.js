// PDF Search Chat Application JavaScript
class PDFChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSubmit(e);
            }
        });
        
        // Example query listeners
        document.querySelectorAll('.example-query').forEach(button => {
            button.addEventListener('click', (e) => {
                this.chatInput.value = e.target.textContent;
                this.handleSubmit(e);
            });
        });
        
        // Show welcome message
        this.showWelcomeMessage();
    }
    
    showWelcomeMessage() {
        const welcomeHTML = `
            <div class="message bot">
                <div class="message-content">
                    <p>👋 Welcome to the PDF Search System!</p>
                    <p>I can help you search through your PDF documents. Ask me about:</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>GDPR compliance requirements</li>
                        <li>Data protection rights</li>
                        <li>Processing agreements</li>
                        <li>Individual rights</li>
                        <li>And much more!</li>
                    </ul>
                    <p>Try one of these example queries:</p>
                    <div class="example-queries">
                        <span class="example-query">What are individual rights under GDPR?</span>
                        <span class="example-query">Data processing agreement requirements</span>
                        <span class="example-query">GDPR compliance checklist</span>
                        <span class="example-query">Personal data breach procedures</span>
                    </div>
                </div>
            </div>
        `;
        this.chatMessages.innerHTML = welcomeHTML;
        
        // Re-attach event listeners to example queries
        document.querySelectorAll('.example-query').forEach(button => {
            button.addEventListener('click', (e) => {
                this.chatInput.value = e.target.textContent;
                this.handleSubmit(e);
            });
        });
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const query = this.chatInput.value.trim();
        if (!query) return;
        
        // Clear input and disable button
        this.chatInput.value = '';
        this.sendButton.disabled = true;
        this.sendButton.textContent = 'Searching...';
        
        // Add user message
        this.addMessage(query, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send request to API
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    max_results: 5,
                    include_highlights: true
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            if (data.success && data.results && data.results.length > 0) {
                this.addSearchResults(data);
            } else {
                this.addMessage(
                    data.error || `I couldn't find any relevant information about "${query}". Please try rephrasing your question or using different keywords.`,
                    'bot',
                    true
                );
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.removeTypingIndicator();
            this.addMessage(
                'Sorry, I encountered an error while searching. Please try again.',
                'bot',
                true
            );
        } finally {
            // Re-enable button
            this.sendButton.disabled = false;
            this.sendButton.textContent = 'Send';
            this.chatInput.focus();
        }
    }
    
    addMessage(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isError) {
            contentDiv.className += ' error-message';
        }
        
        contentDiv.innerHTML = content;
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addSearchResults(data) {
        const resultsHTML = this.formatSearchResults(data);
        this.addMessage(resultsHTML, 'bot');
    }
    
    formatSearchResults(data) {
        const { query, total_results, results } = data;
        
        let html = `<p><strong>Found ${total_results} result${total_results !== 1 ? 's' : ''} for "${query}":</strong></p>`;
        
        results.forEach((result, index) => {
            html += `
                <div class="search-result">
                    <h4>📄 ${result.file_name}</h4>
                    <div class="meta">
                        Page ${result.page_number} • Relevance: ${(result.relevance_score * 100).toFixed(1)}%
                    </div>
                    <div class="content">
                        ${result.highlighted_text || result.text}
                    </div>
                    <a href="${result.url}" target="_blank" class="pdf-link">
                        📖 Open PDF at Page ${result.page_number}
                    </a>
                </div>
            `;
        });
        
        return html;
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-content">
                <span>Searching documents</span>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PDFChatApp();
});

// Handle PDF link clicks (for better user experience)
document.addEventListener('click', (e) => {
    if (e.target.matches('a[href^="file://"]')) {
        e.preventDefault();
        
        // Show a helpful message about opening local files
        const message = `
            <div class="message bot">
                <div class="message-content">
                    <p><strong>📂 Opening Local PDF File</strong></p>
                    <p>To open this PDF file:</p>
                    <ol style="margin: 10px 0; padding-left: 20px;">
                        <li>Copy this path: <code style="background: #f0f0f0; padding: 2px 4px; border-radius: 3px;">${e.target.href}</code></li>
                        <li>Paste it into your browser's address bar</li>
                        <li>Or open the file directly from your file system</li>
                    </ol>
                    <p><em>Note: Browser security settings may prevent direct file:// links from opening.</em></p>
                </div>
            </div>
        `;
        
        document.getElementById('chatMessages').insertAdjacentHTML('beforeend', message);
        document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
    }
});
