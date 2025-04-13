# 🚀 Binance Trading Bot

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A Python-based cryptocurrency trading bot that connects to the Binance exchange for automated trading, real-time market monitoring, and technical analysis.

## 📌 Project Overview

This project implements a full-stack cryptocurrency trading platform using Flask as the web framework. The system includes user authentication, real-time data updates, and automated trading capabilities through WebSocket connections to Binance.

### 🚀 Key Features

- User registration and login system with IP ban protection
- Real-time trade monitoring dashboard
- Technical analysis indicators (RSI, MACD)
- Automated buy/sell orders based on profit thresholds
- JSON endpoints for updating trade data and ticker information

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/binance-trading-bot.git
cd binance-trading-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration file (`config.py`):
- API keys from Binance exchange
- Trading parameters and settings

## 📊 Technical Analysis

The bot uses two main technical indicators:

1. **Relative Strength Index (RSI)**
   - Measures market momentum
   - Typically used to identify overbought/oversold conditions

2. **Moving Average Convergence Divergence (MACD)**
   - Identifies trend direction and potential reversals
   - Composed of MACD line, signal line, and histogram

## 📝 Usage Instructions

1. Configure API keys in `config.py`
2. Start the Flask application:
```bash
python app.py
```

3. Access the web interface at `http://localhost:5000`

4. Monitor real-time market data and trading activity through the dashboard

## 🔧 Development Notes

- The project uses a modular architecture with separate files for different functionalities
- Technical analysis indicators are implemented in their respective modules
- WebSocket connections handle real-time market updates
- Error handling and logging are implemented throughout the codebase

## 📄 License Information

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Please feel free to check out our [contributing guidelines](CONTRIBUTING.md).

---

For more information or to report issues, please visit our GitHub repository.

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-yellow)](https://github.com/yourusername/binance-trading-bot/issues)
[![GitHub Stars](https://img.shields.io/badge/GitHub-Stars-0DFF00.svg)](https://github.com/yourusername/binance-trading-bot/stargazers)