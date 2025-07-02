const express = require('express');
const axios = require('axios');
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');
const router = express.Router();

// In-memory storage for chat sessions (in production, use Redis or database)
const chatSessions = new Map();

// Validation schemas
const messageSchema = Joi.object({
  message: Joi.string().required().min(1).max(1000),
  session_id: Joi.string().optional(),
  sessionId: Joi.string().optional(),
  context: Joi.object().optional()
});

const sessionSchema = Joi.object({
  sessionId: Joi.string().required()
});

// Initialize chat session (frontend expects /start)
router.post('/start', (req, res) => {
  const sessionId = uuidv4();
  const session = {
    id: sessionId,
    createdAt: new Date(),
    messages: [],
    context: {
      userPreferences: {},
      stockInterests: [],
      lastQuery: null
    }
  };
  
  chatSessions.set(sessionId, session);
  
  res.json({
    session_id: sessionId,
    message: 'Chat session initialized successfully'
  });
});

// Send message to chatbot (frontend expects /send)
router.post('/send', async (req, res) => {
  try {
    const { error, value } = messageSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { message, session_id, context } = value;
    
    // Get or create session
    let session = chatSessions.get(session_id);
    if (!session) {
      const newSessionId = uuidv4();
      session = {
        id: newSessionId,
        createdAt: new Date(),
        messages: [],
        context: context || {}
      };
      chatSessions.set(newSessionId, session);
    }

    // Add user message to session
    const userMessage = {
      id: uuidv4(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    
    session.messages.push(userMessage);

    // Send to AI service
    const aiResponse = await axios.post(`${process.env.AI_SERVICE_URL}/chat`, {
      message,
      sessionId: session.id,
      context: session.context,
      history: session.messages.slice(-10) // Last 10 messages for context
    });

    // Add AI response to session
    const botMessage = {
      id: uuidv4(),
      type: 'bot',
      content: aiResponse.data.response,
      confidence: aiResponse.data.confidence,
      suggestions: aiResponse.data.suggestions || [],
      timestamp: new Date()
    };
    
    session.messages.push(botMessage);
    session.context = aiResponse.data.updatedContext || session.context;

    res.json({
      session_id: session.id,
      response: botMessage.content,
      confidence: botMessage.confidence,
      suggestions: botMessage.suggestions,
      context: session.context
    });

  } catch (error) {
    console.error('Error processing chat message:', error.message);
    res.status(500).json({ error: 'Failed to process message' });
  }
});

// Initialize chat session (legacy endpoint)
router.post('/session', (req, res) => {
  const sessionId = uuidv4();
  const session = {
    id: sessionId,
    createdAt: new Date(),
    messages: [],
    context: {
      userPreferences: {},
      stockInterests: [],
      lastQuery: null
    }
  };
  
  chatSessions.set(sessionId, session);
  
  res.json({
    sessionId,
    message: 'Chat session initialized successfully'
  });
});

// Send message to chatbot (legacy endpoint)
router.post('/message', async (req, res) => {
  try {
    const { error, value } = messageSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { message, sessionId, context } = value;
    
    // Get or create session
    let session = chatSessions.get(sessionId);
    if (!session) {
      const newSessionId = uuidv4();
      session = {
        id: newSessionId,
        createdAt: new Date(),
        messages: [],
        context: context || {}
      };
      chatSessions.set(newSessionId, session);
    }

    // Add user message to session
    const userMessage = {
      id: uuidv4(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    
    session.messages.push(userMessage);

    // Send to AI service
    const aiResponse = await axios.post(`${process.env.AI_SERVICE_URL}/chat`, {
      message,
      sessionId: session.id,
      context: session.context,
      history: session.messages.slice(-10) // Last 10 messages for context
    });

    // Add AI response to session
    const botMessage = {
      id: uuidv4(),
      type: 'bot',
      content: aiResponse.data.response,
      confidence: aiResponse.data.confidence,
      suggestions: aiResponse.data.suggestions || [],
      timestamp: new Date()
    };
    
    session.messages.push(botMessage);
    session.context = aiResponse.data.updatedContext || session.context;

    res.json({
      sessionId: session.id,
      response: botMessage.content,
      confidence: botMessage.confidence,
      suggestions: botMessage.suggestions,
      context: session.context
    });

  } catch (error) {
    console.error('Error processing chat message:', error.message);
    res.status(500).json({ error: 'Failed to process message' });
  }
});

// Get chat history
router.get('/history/:sessionId', (req, res) => {
  try {
    const { error, value } = sessionSchema.validate({ sessionId: req.params.sessionId });
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const session = chatSessions.get(value.sessionId);
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }

    res.json({
      sessionId: session.id,
      messages: session.messages,
      context: session.context,
      createdAt: session.createdAt
    });

  } catch (error) {
    console.error('Error fetching chat history:', error.message);
    res.status(500).json({ error: 'Failed to fetch chat history' });
  }
});

// Get chat suggestions
router.get('/suggestions/:sessionId', async (req, res) => {
  try {
    const session = chatSessions.get(req.params.sessionId);
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }

    const response = await axios.get(`${process.env.AI_SERVICE_URL}/chat/suggestions`, {
      params: {
        sessionId: session.id,
        context: session.context
      }
    });

    res.json(response.data);

  } catch (error) {
    console.error('Error fetching suggestions:', error.message);
    res.status(500).json({ error: 'Failed to fetch suggestions' });
  }
});

// Update chat context
router.put('/context/:sessionId', (req, res) => {
  try {
    const session = chatSessions.get(req.params.sessionId);
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }

    session.context = { ...session.context, ...req.body };
    chatSessions.set(session.id, session);

    res.json({
      message: 'Context updated successfully',
      context: session.context
    });

  } catch (error) {
    console.error('Error updating context:', error.message);
    res.status(500).json({ error: 'Failed to update context' });
  }
});

// Clear chat session
router.delete('/session/:sessionId', (req, res) => {
  try {
    const deleted = chatSessions.delete(req.params.sessionId);
    if (!deleted) {
      return res.status(404).json({ error: 'Session not found' });
    }

    res.json({ message: 'Session cleared successfully' });

  } catch (error) {
    console.error('Error clearing session:', error.message);
    res.status(500).json({ error: 'Failed to clear session' });
  }
});

module.exports = router; 