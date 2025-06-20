const userService = require('../services/userService');

const userController = {
  async register(req, res) {
    try {
      const user = await userService.register(req.body);
      res.status(201).json({
        message: 'User registered successfully',
        user: {
          id: user._id,
          name: user.name,
          email: user.email
        }
      });
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async login(req, res) {
    try {
      const { email, password } = req.body;
      const result = await userService.login(email, password);
      res.json(result);
    } catch (error) {
      res.status(401).json({ message: error.message });
    }
  },

  async getProfile(req, res) {
    try {
      const user = await userService.getUserProfile(req.user.userId);
      res.json(user);
    } catch (error) {
      res.status(404).json({ message: error.message });
    }
  },

  async updateProfile(req, res) {
    try {
      const user = await userService.updateUserProfile(req.user.userId, req.body);
      res.json(user);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async changePassword(req, res) {
    try {
      const { currentPassword, newPassword } = req.body;
      const result = await userService.changePassword(
        req.user.userId,
        currentPassword,
        newPassword
      );
      res.json(result);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async deleteAccount(req, res) {
    try {
      const { password } = req.body;
      const result = await userService.deleteAccount(req.user.userId, password);
      res.json(result);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }
};

module.exports = userController; 