# ScubaDiveDubai

## Intro

Welcome to ScubaDiveDubai. This is an E-Commerce application powered by Python using the django framework.

Dummy user details:

- Username: cooluser
- Password: admin

## Basic functionality

- See all items for sale on landing page
- Filter by categories
- Sign in or Sign up
  - When signing up a signal is triggered to create a new ShopProfile for a user, without is a user cannot purchase items
- View individual items
- Add items too cart
  - Check order exists
  - Check items are in the cart then increment or add items
  - Add billing and shipping address, choose to save addresses for next time
- Add a coupon
- Proceed to checkout
- Currently only cash on delivery option available
- Admin interface
  - Upload csv to populate or update stock items, categories and more..
  - Customized admin list views

## Production Plugins

### Django allauth

This is used for user authentication and authorization, it handles all routes and forms with
class based views, the application ships with most sign in and sign up templates

### Django Countries

Allows the choice of countries in checkout view. All auth allows easy user authentication.

### Crispy Forms

Improved form styling using bootstrap4

## Development Plugins

### Django Extensions

Used to track todo's while developing the application

### Gunicorn

Used to run the app on an EC2 instance on AWS

## Technical Overview

### Languages

- Python : Server side controller
- Javascript : Client side functionality and interactivity
- CSS : Originally written in SCSS and compiled to CSS for styling
  - Most styling is handled by template used from MDBootstrap.com
- HTML : Basic webpage layout

### Database

- Currently running SQLite Database

---

#### Created by: Pierre du Toit
