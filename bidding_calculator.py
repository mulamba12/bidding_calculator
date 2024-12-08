import streamlit as st
import pandas as pd

# Default costs and constants
COSTS = {
    "resinous_material_cost_per_sqft": 6.00,
    "sealed_concrete_tub_cost": 800,
    "sealed_concrete_coverage_per_tub": 11000,
    "garage_back_porch_cost_per_sqft": 5.00,
    "new_concrete_cost_per_sqft": 6.25,
    "light_cost": 1500,
    "hoop_cost": 2300,
    "fence_cost_per_foot": 7,
    "net_cost": 200,
    "hourly_wage": 30,
    "mileage_rate": 0.58,
    "lodging_cost_per_day": 150,
    "workday_hours": 8,
}

def calculate_bid_for_job(job_type, square_footage, distance_from_lubbock, desired_profit_margin, num_workers, sports_court_details=None):
    resinous_material_cost_per_sqft = COSTS["resinous_material_cost_per_sqft"]
    sealed_concrete_tub_cost = COSTS["sealed_concrete_tub_cost"]
    sealed_concrete_coverage_per_tub = COSTS["sealed_concrete_coverage_per_tub"]
    hourly_wage = COSTS["hourly_wage"]
    garage_back_porch_cost_per_sqft = COSTS["garage_back_porch_cost_per_sqft"]
    new_concrete_cost_per_sqft = COSTS["new_concrete_cost_per_sqft"]
    light_cost = COSTS["light_cost"]
    hoop_cost = COSTS["hoop_cost"]
    fence_cost_per_foot = COSTS["fence_cost_per_foot"]
    net_cost = COSTS["net_cost"]
    mileage_rate = COSTS["mileage_rate"]
    lodging_cost_per_day = COSTS["lodging_cost_per_day"]
    workday_hours = COSTS["workday_hours"]

    material_cost = 0
    labor_hours = 0
    additional_costs = {
        "fence_cost": 0,
        "light_cost": 0,
        "hoop_cost": 0,
        "net_cost": 0,
    }

    if job_type == "Resinous Flooring":
        material_cost = resinous_material_cost_per_sqft * square_footage
        labor_hours = square_footage / 8
    elif job_type == "Sealed Concrete":
        material_cost = (square_footage / sealed_concrete_coverage_per_tub) * sealed_concrete_tub_cost
        labor_hours = square_footage / 250
    elif job_type == "Garage/Back Porch":
        material_cost = garage_back_porch_cost_per_sqft * square_footage
        labor_hours = workday_hours * 4
    elif job_type == "Sports Courts":
        if sports_court_details["new_concrete"]:
            material_cost += new_concrete_cost_per_sqft * square_footage
        num_courts = sports_court_details["num_courts"]
        if sports_court_details["pickleball"] or sports_court_details["basketball"]:
            if sports_court_details["net"]:
                additional_costs["net_cost"] += net_cost * num_courts
            if sports_court_details["fence"]:
                additional_costs["fence_cost"] += fence_cost_per_foot * square_footage
            if sports_court_details["lights"]:
                additional_costs["light_cost"] += light_cost * 2 * num_courts
            if sports_court_details["basketball"] and sports_court_details["hoop"]:
                additional_costs["hoop_cost"] += hoop_cost * num_courts
        labor_hours = workday_hours * 4
    else:
        return "Invalid job type entered."

    labor_cost = labor_hours * hourly_wage
    total_additional_costs = sum(additional_costs.values())
    total_cost = material_cost + labor_cost + total_additional_costs

    if distance_from_lubbock > 50:
        travel_cost = distance_from_lubbock * mileage_rate * 2
        lodging_days = labor_hours / (num_workers * workday_hours)
        lodging_cost = lodging_days * lodging_cost_per_day
    else:
        travel_cost = 0
        lodging_cost = 0

    total_cost += travel_cost + lodging_cost

    profit_multiplier = 1 + (desired_profit_margin / 100)
    bid_price = total_cost * profit_multiplier

    result = {
        "Job Type": job_type,
        "Square Footage": square_footage,
        "Workers Assigned": num_workers,
        "Material Cost ($)": round(material_cost, 2),
        "Labor Cost ($)": round(labor_cost, 2),
        "Additional Costs": additional_costs,
        "Total Additional Costs ($)": round(total_additional_costs, 2),
        "Travel Cost ($)": round(travel_cost, 2),
        "Lodging Cost ($)": round(lodging_cost, 2),
        "Total Cost (before profit) ($)": round(total_cost, 2),
        "Profit Margin (%)": desired_profit_margin,
        "Bid Price (with profit) ($)": round(bid_price, 2),
    }
    return result

# Streamlit App
st.title("Job Bidding Calculator")
st.sidebar.title("Adjust Costs")

# Adjust Costs
if st.sidebar.checkbox("Adjust Costs"):
    st.sidebar.subheader("Edit Costs")
    for key, value in COSTS.items():
        COSTS[key] = st.sidebar.number_input(f"{key.replace('_', ' ').title()}", value=value)

# Job Details
st.header("Enter Job Details")
job_type = st.selectbox("Select Job Type", ["Resinous Flooring", "Sealed Concrete", "Garage/Back Porch", "Sports Courts"])
square_footage = st.number_input("Square Footage", min_value=0.0)
distance_from_lubbock = st.number_input("Distance from Lubbock (miles)", min_value=0.0)
desired_profit_margin = st.number_input("Profit Margin (%)", min_value=0.0)
num_workers = st.number_input("Number of Workers Assigned", min_value=1)

sports_court_details = {}
if job_type == "Sports Courts":
    sports_court_details["new_concrete"] = st.checkbox("New Concrete Needed")
    sports_court_details["pickleball"] = st.checkbox("For Pickleball")
    sports_court_details["basketball"] = st.checkbox("For Basketball")
    sports_court_details["num_courts"] = st.number_input("Number of Courts", min_value=1)
    sports_court_details["net"] = st.checkbox("Include Net")
    sports_court_details["fence"] = st.checkbox("Include Fence")
    sports_court_details["lights"] = st.checkbox("Include Lights")
    sports_court_details["hoop"] = st.checkbox("Include Basketball Hoop")

if st.button("Calculate Bid"):
    result = calculate_bid_for_job(job_type, square_footage, distance_from_lubbock, desired_profit_margin, num_workers, sports_court_details)
    st.subheader("Job Pricing Summary")
    for key, value in result.items():
        if isinstance(value, dict):  # Handle additional costs breakdown
            st.text(f"{key}:")
            for sub_key, sub_value in value.items():
                st.text(f"  {sub_key.replace('_', ' ').title()}: ${sub_value}")
        else:
            st.text(f"{key}: {value}")
