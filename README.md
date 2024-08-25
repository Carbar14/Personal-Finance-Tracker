# Fiscal Flux

#### Video Demo: <[Youtube Video](https://youtu.be/YN00Vr-a6j0)>

#### Description:

1. **Intro**

- This program is a personal expense and income tracker
- It lets expenses and incomes be added and analyzed
- The navbar on the top allows you to navigate between pages

2. **Login**

- This program allows you to register an account with username and password and it makes sure that the passwords match, the username is not taken, and that you have agreed to the terms of use. If one of these things is not done correctly it will display it with red text. When registering you have the option to stay signed in which makes you stay signed in when logging onto the site for 30 days.
- When you login you can login with the username and password you used to register and you have the option to stay signed in.
- The password is hashed and stored in the database, so it is secure.

3. **Adding Expenses/Incomes**

- In the navbar you can choose to add an expense or income
- Each one brings you to a new page which lets you put in the details for either one.
- Adding expenses lets you:

* Add a new category or select from an existing one
* Enter the description of the expense
* Add a new purchase location or select and existing one
* Input the quantity which is required
* Input the price which is required and it is to 2 decimal places
* Date input for the date the expense incurred
* Display color which changes the color of how it appears on the home page or anywhere else
* A button to change the color to the default white
* A button to change every expense with the category selected to the color that is selected on the color wheel
* A button to add the expense

- Adding incomes lets you:

* Add a new category or select from an existing one
* Enter the description of the income
* Add a new Payment method or select from an existing one
* Input the income value which is required and it is to 2 decimal places
* Date input for the date the income was earned
* Display color which changes the color of how it appears on the home page or anywhere else
* A button to change the color to the default white
* A button to change every income with the category selected to the color that is selected on the color wheel
* A button to add the income

- These expenses and incomes are added to the database and can be seen in the home page, analysis pages, pie chart, and line chart

4. **Home Page**

- Home page will display a link to the page that you can add expenses and incomes if there are none already added
- It will also have a button and a dropdown to upload expenses/incomes from a csv file which will be explained in another section
- Button to download expenses and incomes into csv files
- When there are expenses and incomes it will display them in a big chart displaying all the data in the colors selected
- there is a button on the far right to delete it and a button to edit it which will be explained later

5. **Download .csv File**

- There is a button avaliable on the home page that will download expenses/income (whichever is selected in the dropdown) to your computer in the form of a csv file
- It takes all the data and converts from the database to a csv file with column headers.

6. **Upload .cvs File**

- On the home page there is a upload csv file button and an info button which will explain everything that is required in the .csv file to make it work
- It will upload to expenses or income depending on what is selected in the dropdown
- When uploading it will give warnings if the csv file has wrong headers, wrong file extension etc.
- If successful the upload will convert every row in the csv file into entries into the database and they will immediately be seen in the home page

7. **Analyze**

- The analyze tabs allows you to filter by all the criteria and display whatever fits the filters selected
- Analyze Expenses allows you to:

* Filter by Category
* Filter by Purchase location
* Filter description by keyword
* Filter by exact date
* Filter by from and to date
* Filter by from and to price
* Filter by Color
* Press search button to show the filtered results

- Analyze Incomes allows you to:

* Filter by Category
* Filter by Payment method
* Filter description by keyword
* Filter by exact date
* Filter by from and to date
* Filter by from and to price
* Filter by Color
* Press search button to show the filtered results

- Each page allows you to delete all in search which gives a popup warning, and there is also a delete and edit button for each item
- There is a total of the expenses/incomes in the search

8. **Pie Chart**

- Pie chart allows you to see the percentage of expenses/incomes based on category in pie chart form
- There is a button to switch between expenses and incomes
- There is a year filter which allows you to enter in a year you want to see, a clear year button which gets rid of the filter, and a current year button which sets to year box to the current year.
- There is a month filter which filters the results to a certain month
- Features of Pie Chart:

* A list of categories and their color at the top
* Percentage displayed on each slice
* Values are shown with its category name when hovering on each slice
* Different colors for each slice

- Made with library

9. **Line Chart**

- Line chart lets you see the change in values of expenses and incomes simultaneously over all the months
- Can be filtered by year including all years
- Respective expense and income category filters can be set to none (displaying no expenses/incomes respectively), All (displaying all categories of expense/incomes respectively), and each category can be selected or deselected, allowing multiple to be selected at a time.
- Features of the Line Chart:

* X-axis is labeled with months
* Y-axis is labeled with monetary value
* Red line for expenses and blue line for income, which has a legend on the top

- Made with library

## File Breakdown

- **Templates**

* addExpense.html

- contains all necessary html, jinja, and javascript to display add expense page

* addIncome.html

- contains all necessary html, jinja, and javascript to display add income page

* analyzeExpenses.html

  - contains all necessary html, jinja, and javascript to display analyze expenses page

* analyzeIncome.html

  - contains all necessary html, jinja, and javascript to display analyze incomes page

* base.html

  - base has the site head including the title and any fonts, my css, bootsrap css, and bootsrap javascript
  - the layout template is nested inside this when logged in, and when not, the login/register template is nested in it.

* editExpense.html

  - contains all necessary html, jinja, and javascript to display edit expense page

* editIncome.html

  - contains all necessary html, jinja, and javascript to display edit income page

* index.html

  - contains all necessary html, jinja, and javascript to display the home page

* layout.html

  - layout is used after login to display full navbar with all the links to each page
  - every page that is used when the user is logged in is nested inside this template so that the navbar is always seen

* lineChart.html

  - contains all necessary html, jinja, and javascript (with chart library) to display line chart page

* login.html

  - contains all necessary html, jinja, and javascript (with chart library) to display login page and limited nav bar

* pieChart.html

  - contains all necessary html, jinja, and javascript (with chart library) to display pie chart page

* register.html

  - contains all necessary html, jinja, and javascript to display the register page and limited nav bar

* uploadInfo.html

  - contains all necessary html, jinja, and javascript (with chart library) to display the upload info page

- **CSS.css**

* All custom class and tag styles for different items located throughout the pages

- **setup.sql**

* Sets up three tables in the database:

- Users which stores each user including its id, username and hashed password
- Expenses which stores the id, user id, and all necessary information for the expense
- Incomes which stores the id, user id, and all necessary information for the expense

- **init_db.py**

* This python file is run to execute the setup.sql file

- **helpers.py**

* This python file has a couple functions that are used in app.py

- get_db_connection gets connection to database
- login_required makes it so that login is required to see certain pages
