# Merge SFDC Accounts

This is a simple script using Salesforce.com's REST API to merge accounts.

## Overview

In its current form, the script does the following:
* Authenticates the user using simple_salesforce and credentials stored in environment variables.
* Loads list of accounts is loaded from a CSV-file with these columns:
  1. Id
  1. Name
  1. BillingPostalCode
* Groups accounts with the same name and billing postal code.
* Merges the first two accounts in each group via a REST API request. (If there are more than two accounts with the same name and postal code, only the first two will be merged.)
* Saves the API responses to a text-file.
