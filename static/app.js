// Daily Creator AI - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.getElementById('registrationForm');
    const demoBtn = document.getElementById('demoBtn');
    const demoResults = document.getElementById('demoResults');

    // Registration form submission
    registrationForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = registrationForm.querySelector('.submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        
        try {
            // Collect form data
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                skills: document.getElementById('skills').value.split(',').map(s => s.trim()),
                interests: document.getElementById('interests').value.split(',').map(s => s.trim()),
                goals: document.getElementById('goals').value.split(',').map(s => s.trim()),
                github_username: document.getElementById('github').value || null,
                email_time: document.getElementById('emailTime').value
            };
            
            // Submit registration
            const response = await fetch('/api/users/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('success', `Welcome ${formData.name}! Your account has been created successfully. Check your email for your first recommendations!`);
                
                // Generate recommendations
                await generateRecommendations(result.user_id);
                
            } else {
                showMessage('error', result.detail || 'Registration failed. Please try again.');
            }
            
        } catch (error) {
            console.error('Registration error:', error);
            showMessage('error', 'Network error. Please check your connection and try again.');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    });

    // Demo simulation
    demoBtn.addEventListener('click', async function() {
        demoBtn.disabled = true;
        demoBtn.textContent = 'Running Demo...';
        
        try {
            const response = await fetch('/api/demo/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                displayDemoResults(result);
            } else {
                showMessage('error', result.detail || 'Demo failed. Please try again.');
            }
            
        } catch (error) {
            console.error('Demo error:', error);
            showMessage('error', 'Demo failed. Please try again.');
        } finally {
            demoBtn.disabled = false;
            demoBtn.textContent = 'Run Demo Simulation';
        }
    });

    // Generate recommendations for registered user
    async function generateRecommendations(userId) {
        try {
            const response = await fetch(`/api/users/${userId}/recommendations/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('info', `Generated ${result.total_count} personalized recommendations! Check your email for the full details.`);
                displayRecommendations(result.recommendations);
            } else {
                showMessage('error', 'Failed to generate recommendations. Please try again.');
            }
            
        } catch (error) {
            console.error('Recommendation generation error:', error);
            showMessage('error', 'Failed to generate recommendations. Please try again.');
        }
    }

    // Display demo results
    function displayDemoResults(result) {
        demoResults.innerHTML = `
            <h4>🎬 Demo Results</h4>
            <div class="demo-info">
                <p><strong>User ID:</strong> ${result.user_id}</p>
                <p><strong>Recommendations Generated:</strong> ${result.recommendations.total_count}</p>
            </div>
            <div class="recommendations-preview">
                <h5>Sample Recommendations:</h5>
                ${result.recommendations.recommendations.map(rec => `
                    <div class="recommendation-item">
                        <h6>${rec.title}</h6>
                        <p>${rec.description}</p>
                        <div class="rec-meta">
                            <span class="category">${rec.category}</span>
                            <span class="difficulty">${rec.difficulty_level}</span>
                            <span class="score">Score: ${Math.round(rec.score * 100)}%</span>
                        </div>
                    </div>
                `).join('')}
            </div>
            <p class="demo-note">💡 This is a demo simulation. In the real system, you would receive a beautiful email with these recommendations!</p>
        `;
        demoResults.style.display = 'block';
    }

    // Display recommendations
    function displayRecommendations(recommendations) {
        const recommendationsHtml = recommendations.map(rec => `
            <div class="recommendation-item">
                <h6>${rec.title}</h6>
                <p>${rec.description}</p>
                <div class="rec-meta">
                    <span class="category">${rec.category}</span>
                    <span class="difficulty">${rec.difficulty_level}</span>
                    <span class="score">Score: ${Math.round(rec.score * 100)}%</span>
                </div>
                <div class="next-steps">
                    <strong>Next Steps:</strong>
                    <ul>
                        ${rec.next_steps.map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `).join('');

        const recommendationsSection = document.createElement('section');
        recommendationsSection.className = 'recommendations-section';
        recommendationsSection.innerHTML = `
            <h3>Your Recommendations</h3>
            <div class="recommendations-list">
                ${recommendationsHtml}
            </div>
        `;

        // Insert after the registration form
        registrationForm.parentNode.insertBefore(recommendationsSection, registrationForm.nextSibling);
    }

    // Show message to user
    function showMessage(type, message) {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.message');
        existingMessages.forEach(msg => msg.remove());

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        // Insert after header
        const header = document.querySelector('.header');
        header.insertAdjacentElement('afterend', messageDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    // Add some interactive effects
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Form validation
    const inputs = document.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                this.style.borderColor = '#ef4444';
            } else {
                this.style.borderColor = '#e5e7eb';
            }
        });
    });
});
