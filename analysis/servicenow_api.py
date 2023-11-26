import requests
import pandas as pd
from matplotlib import pyplot as plt


class API:
    def __init__(
        self,
        base_url="https://dev218227.service-now.com/api/now/table/incident?sysparm_fields={0}",
    ):
        """
        Initialize JokeAPI with a base URL for API requests.

        Parameters:
        - base_url (str): Base URL for the API requests.
        """
        self.base_url = base_url

    def api_response(self):
        """
        Make an API request and return the response as a DataFrame.

        Returns:
        - pd.DataFrame: DataFrame containing API response data.
        """
        # Parse the JSON response
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        user = "admin"
        pwd = "!61ookqAPG@D"
        sys_params = "number,contact_type,state,impact,sys_created_by,opened_at,priority,resolved_at,closed_at,short_description,close_code,subcategory,escalation,category,urgency,resolved_by,reopen_count,assigned_to"
        response = requests.get(
            self.base_url.format(sys_params), auth=(user, pwd), headers=headers
        )

        # Check if the request was successful
        if response.status_code == 200:
            records = response.json()
            output = records["result"]
            df = pd.json_normalize(output)
            return df

    def columns_orderby(self):
        """
        Clean columns of the DataFrame obtained from the API response.

        Returns:
        - pd.DataFrame: DataFrame with cleaned columns.
        """
        df = self.api_response()

        # Remove columns with all null values
        remove_null_columns = df.dropna(axis=1, how="all")

        # Select specific columns for analysis
        sys_params = [
            "number",
            "impact",
            "contact_type",
            "sys_created_by",
            "opened_at",
            "priority",
            "impact",
            "urgency",
            "assigned_to",
            "resolved_at",
            "closed_at",
            "short_description",
            "close_code",
            "subcategory",
            "escalation",
            "category",
            "resolved_by",
            "reopen_count",
        ]
        data = df[sys_params]

        # Display first rows, info, and description of the selected columns
        first_rows = data.head()
        data_info = data.info()
        data_description = data.describe()

        print(first_rows)
        print(data_info)
        print(data_description)

        return data

    def ticket_status_analysis(self):
        """
        Perform analysis on the DataFrame obtained from the API response and visualize the results.
        """
        df = self.api_response()

        # Count occurrences of each priority
        priority_counts = df["state"].value_counts()

        # Display the distribution of incident priorities
        print("Distribution of Incident Priorities:")
        print(priority_counts)

        ax = priority_counts.sort_index().plot(
            kind="bar", title="Incident Tickets state"
        )

        # Customize x-axis labels using a mapping
        state_labels = {
            1: "NEW",
            2: "In Progress",
            3: "ON HOLD",
            6: "Resolved",
            7: "Closed",
        }
        ax.set_xticklabels(
            [state_labels[int(state)] for state in priority_counts.sort_index().index],
            rotation=45,
            ha="right",
        )

        plt.show()

    def contacted_for_incident_analysis(self):
        df = self.api_response()

        # Count the occurrences of each incident contact type
        df["contact_type"] = df["contact_type"].replace(["", None], "Not filled")
        contact_type_counts = df["contact_type"].value_counts()

        # Create a pie chart for incident contact types
        plt.figure(figsize=(8, 8))
        plt.pie(
            contact_type_counts,
            labels=contact_type_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Accent.colors,
        )
        plt.title("Distribution of Incident Contact Types")
        plt.show()

    def priority_analysis(self):
        df = self.api_response()

        # Create a pivot table to count occurrences of each priority for each root cause
        pivot_table = pd.pivot_table(
            df,
            values="number",
            index="category",
            columns="priority",
            aggfunc="count",
            fill_value=0,
        )
        pivot_table.index = pivot_table.index.where(
            pivot_table.index != "", "Other Category"
        )

        # Visualize the data with a stacked bar chart
        ax = pivot_table.plot(kind="bar", figsize=(12, 8))

        ax.set_xlabel("Root Cause")
        ax.set_ylabel("Count")
        ax.set_title("Distribution of Incident Priorities for Each Root Cause")

        plt.legend(title="Priority")
        plt.show()
