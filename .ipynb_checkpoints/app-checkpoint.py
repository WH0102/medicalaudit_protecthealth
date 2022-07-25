import streamlit as st
st.set_page_config(page_title = "Medical Audit Presentation", layout = "wide")
import pandas as pd
import numpy as np
from datetime import date,timedelta
import plotly.express as px
px.set_mapbox_access_token("pk.eyJ1IjoibWFuZnllIiwiYSI6ImNrN2hvc3h1ejBjcWszZ25raXk0Z3VqaTkifQ.5PHi84GwoNUG5v-GMHZP1w")

col1, col2 = st.columns(2)
with col1:
    st.progress(100)
    st.title("TCMC Presentation by MAS ")
    st.subheader("on {}".format(date.today().strftime("%d-%m-%Y")))
    st.progress(100)
with col2:
    uploaded_file = st.file_uploader("Please upload post analysis file only.")

# Trial to set is the file not empty then set  df
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header = 0, sheet_name = "raw")
    df.loc[:,"hs1_created_date"] = pd.to_datetime(df.loc[:,"hs1_created_date"]).dt.strftime("%d/%m/%y")
    df.loc[:,"hs2_created_date"] = pd.to_datetime(df.loc[:,"hs2_created_date"]).dt.strftime("%d/%m/%y")
    
    # Create side bar
    st.sidebar.write("Choose 1 to present")

    slide_types = st.sidebar.radio("Choose recommendation", 
                                   ("Overall Summary",) + 
                                   tuple(df.sort_values("slide_type", 
                                                        key = lambda x: x.map({"k_issue":1,
                                                                               "hs2_issue":2,
                                                                               "pdpa_issue":3,
                                                                               "diagnosis_issue":4,
                                                                               "ufeme_issue":5,
                                                                               "no_section_k":6,
                                                                               "incomplete_section":7,
                                                                               "incomplete_result":8,
                                                                               "delete":9}))\
                                           .loc[:,"slide_type"].unique().transpose()) + 
                                   ("Provider Watchlist", "Financial Summary"))
    
    # Function for presentation
    def presentation(left_upper, right_upper, table, recommendation):
        st.progress(100)
        col1, col2 = st.columns(2)
        with col1:
            st.container().header(left_upper)
        with col2:
            st.container().code(right_upper)
        st.table(table)
        st.subheader("MAS Recommendation =")
        st.code(recommendation)
        st.progress(100)
        
    # First Slide
    if slide_types == "Overall Summary":
        st.subheader("Distribution of Claim IDs that escalated to MAS based on provider type. (n={})".format(len(df)))
        st.plotly_chart(px.pie(df.drop_duplicates(subset = "provider_id")\
                                 .pivot_table(index = "provider_type",
                                              values = "provider_id",
                                              aggfunc = len,
                                              margins = False)\
                                 .rename_axis(None, axis = 1).reset_index().rename(columns = {"provider_id":"Total"}), 
                               height = 700,
                               values = "Total", 
                               names = "provider_type")\
                          .update_traces(textposition = 'auto', 
                                         insidetextorientation = "horizontal",
                                         textinfo = 'percent+label+value', 
                                         textfont_size = 30, 
                                         sort = False, 
                                         rotation = 45)\
                          .update(layout_showlegend = False), use_container_width=True)
        
        st.subheader("Distribution of Claim IDs that escalated to MAS based on Completeness of Investigation Reports. (n={})".format(len(df)))
        df.loc[:,"ix_complete3"] = "Incomplete Investigation Results"
        df.loc[df.loc[:,"ix_complete"] == "Complete", "ix_complete3"] = "Complete Investigation Results"
        df.loc[df.loc[:,"ix_complete"] == "No Result", "ix_complete3"] = "No Investigation Result Uploaded"
        st.plotly_chart(px.pie(df.pivot_table(index = "ix_complete3",
                                              values = "provider_id",
                                              aggfunc = len,
                                              margins = False)\
                                 .rename_axis(None, axis = 1).reset_index().rename(columns = {"provider_id":"Total"}), 
                               height = 700,
                               values = "Total", 
                               names = "ix_complete3")\
                          .update_traces(textposition = 'auto', 
                                         insidetextorientation = "horizontal",
                                         textinfo = 'percent+label+value', 
                                         textfont_size = 30, 
                                         sort = False, 
                                         rotation = 45)\
                          .update(layout_showlegend = False), use_container_width=True)
        
        st.subheader("Distribution of Claim IDs that escalated to MAS based on MAS Recommendation. (n={})".format(len(df)))
        st.table(df.pivot_table(index = "recommendation",
                                values = "claim_id",
                                aggfunc = len,
                                margins = True)\
                   .rename(index = {"re_up_pdpa": "Request provider to Re-upload PDPA",
                                    "exempted_crm": "Exempted after Obtain Verbal Consent",
                                    "archive_pdpa": "Long Pending Cases (PDPA)",
                                    "verbal": "To Pay after Obtain Verbal Consent",
                                    "pay": "To Pay"},
                           columns = {"claim_id":"Total Claim ID"})\
                   .sort_values("Total Claim ID"))
        
        st.subheader("Distribution of Claim IDs that escalated to MAS based on claim condition. (n={})".format(len(df)))
        st.table(df.pivot_table(index = ["ix_complete2", "diagnosis2"],
                                columns = ["pdpa_acceptance", "section_done"],
                                values = "claim_id", 
                                aggfunc = len,
                                margins = True)\
                       .fillna(0).astype(int))
    
    # For Provider Watchlist
    elif slide_types == "Provider Watchlist":
        st.subheader("Update on Provider Watchlist:")
        # The main table
        pw = pd.read_excel(uploaded_file, header = 0, sheet_name = "provider_watchlist")
        pw.loc[:,("issue_claims", "pdpa", "section", "ix", "k_lysed", "no_ufeme", "dx", "hs2_issue")] = pw.loc[:,("issue_claims", "pdpa", "section", "ix", "k_lysed", "no_ufeme", "dx", "hs2_issue")]\
                                                                                                          .fillna(0)\
                                                                                                          .apply(lambda x: pd.to_numeric(x, downcast = "integer"), 
                                                                                                                 axis = 1)
        pw.loc[:,"min_date"] = pd.to_datetime(pw.loc[:,"min_date"]).dt.strftime("%d/%m/%y")
        pw.loc[:,"max_date"] = pd.to_datetime(pw.loc[:,"max_date"]).dt.strftime("%d/%m/%y")
        pw = pw.fillna("None")
        st.dataframe(pw)
        
        # The brief summary on movement
        st.subheader("Summary of provider movement in provider watchlist.")
        st.table(pw.pivot_table(index = ["colour", "next_colour"],
                                values = "provider_id",
                                aggfunc = len,
                                margins = False)\
                   .rename_axis(None, axis = 1).reset_index()\
                    .rename(columns = {"provider_id":"Number of Providers"}))
        
    # For Financial Summary
    elif slide_types == "Financial Summary":
        st.header("Financial Summary")
        st.table(df.pivot_table(index = ["recommend", "ix_complete2"],
                                values = "pay_hs1",
                                aggfunc = sum, 
                                fill_value = 0,
                                margins = True)\
                    .merge(df.pivot_table(index = ["recommend", "ix_complete2"], 
                                          values = "pay_hs2",
                                          aggfunc = sum,
                                          fill_value = 0,
                                          margins = True), 
                           how = "outer", left_index = True, right_index = True)\
                    .merge(df.pivot_table(index = ["recommend", "ix_complete2"], 
                                          values = "pay_lab",
                                          aggfunc = sum,
                                          fill_value = 0,
                                          margins = True), 
                           how = "outer", left_index = True, right_index = True)\
                    .sort_values('recommend', key=lambda x: x.map({"To Pay": 1, 
                                                                   "Verbal Consent/ Re-upload PDPA": 2, 
                                                                   "Others": 3,
                                                                   "All":4})))
        st.header("Total = RM {}".format(round(df.loc[:,("pay_hs1", "pay_hs2", "pay_lab")].sum(axis = 0).sum()), 0))
        
    # For Potassium Lysed Issue
    elif slide_types == "k_issue":
        num = 1
        for provider in df.loc[df.loc[:,"slide_type"] == "k_issue", "provider_id"].sort_values().unique():
            presentation("{}. Provider ID = {}, {}, from {}, (n = {}) \n Distance Between Provider And Lab = {}km"\
                             .format(num, provider, 
                                     df.loc[df.loc[:,"provider_id"] == provider, "provider_name"].min(),
                                     df.loc[df.loc[:,"provider_id"] == provider, "lab_state"].reset_index().loc[0,"lab_state"],
                                     len(df.loc[((df.loc[:,"slide_type"] == "k_issue") & (df.loc[:,"provider_id"] == provider))]),
                                     df.loc[df.loc[:,"provider_id"] == provider, "distance"].min()),
                         "- Complete PDPA/ Incomplete PDPA (No Date Only) \n" +
                         "- 3/3 Sections Done \n" +
                         "- Complete Result Uploaded \n" +
                         "- Correct Diagnosis",
                         df.loc[((df.loc[:,"slide_type"] == "k_issue") & 
                                 (df.loc[:,"provider_id"] == provider))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "payment_lab", "ix_justification")],
                         df.loc[((df.loc[:,"slide_type"] == "k_issue") & 
                                 (df.loc[:,"provider_id"] == provider)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            provider_geo = df.loc[((df.loc[:,"slide_type"] == slide_types) & 
                                   (df.loc[:,"provider_id"] == provider)), 
                                   ("provider_id", "provider_name", "provider_type", "provider_lat", "provider_lng")].drop_duplicates(subset = "provider_id")
            lab_geo = df.loc[((df.loc[:,"slide_type"] == slide_types) & 
                              (df.loc[:,"provider_id"] == provider)),
                              ("lab_id", "lab_name", "provider_type", "lab_lat", "lab_lng")].drop_duplicates(subset = "lab_id")\
                        .rename(columns = {"lab_id": "provider_id",
                                           "lab_name": "provider_name",
                                            "lab_lat": "provider_lat",
                                            "lab_lng": "provider_lng"})
            lab_geo.loc[:,"provider_type"] = "Lab"
            geo_temp = pd.concat([provider_geo, lab_geo], ignore_index = True)
            geo_temp.loc[:,"size"] = 10
                             
            # st.write(geo_temp)
            st.plotly_chart(px.scatter_mapbox(geo_temp, lat = "provider_lat", lon = "provider_lng", color = "provider_type", size = "size"), use_container_width=True)
            num += 1
            
    # For HS2 Issues
    elif slide_types == "hs2_issue":
        num = 1
        for recommendation in df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                      (df.loc[:,"ix_complete"] == "Complete"))]\
                                .sort_values("recommendation", key = lambda x: x.map({"pay":1,
                                                                                      "exempted":2}))\
                                .loc[:,"recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                                              (df.loc[:,"ix_complete"] == "Complete") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                        "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                                       (df.loc[:,"ix_complete"] == "Complete") & 
                                                       (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                                    "- 3/3 Sections Done \n" +
                                    "- Complete Result Uploaded \n" +
                                    "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                                                (df.loc[:,"ix_complete"] == "Complete") & 
                                                                (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                         df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                 (df.loc[:,"ix_complete"] == "Complete") & 
                                 (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs2_created_date", "hs2_issue", "payment_hs1", "payment_lab", "hs2_justification", "normal_diag")],
                        df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                (df.loc[:,"ix_complete"] == "Complete") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
        if len(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                       (df.loc[:,"ix_complete"] == "No UFEME"))]) >=1:
            for recommendation in df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                          (df.loc[:,"ix_complete"] == "No UFEME"))]\
                                .sort_values("recommendation", key = lambda x: x.map({"pay":1,
                                                                                      "exempted":2}))\
                                .loc[:,"recommendation"].unique():
                presentation("{}. {} for No UFEME claims (n = {})".format(num, recommendation,
                                                                                   len(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                                                                               (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                                                               (df.loc[:,"recommendation"] == recommendation))])),
                            "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                                                   (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                                   (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                                    "- 3/3 Sections Done \n" +
                                    "- No UFEME only (Other parameters complete) \n" +
                                    "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                                                (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                                (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                            df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                    (df.loc[:,"ix_complete"] == "No UFEME") & 
                                    (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                              .loc[:,("claim_id", "provider_id", "provider_name", "hs2_created_date", "hs2_issue", "payment_hs1", "payment_lab", "hs2_justification", "ix_justification", "normal_diag")],
                            df.loc[((df.loc[:,"slide_type"] == "hs2_issue") & 
                                    (df.loc[:,"ix_complete"] == "No UFEME") & 
                                    (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
                num += 1
                
    # For PDPA Issues
    elif slide_types == "pdpa_issue":
        num = 1
        for recommendation in df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                      (df.loc[:,"ix_complete"] == "Complete"))]\
                                .sort_values("recommendation", 
                                             key = lambda x: x.map({"pay":1,
                                                                    "verbal":2,
                                                                    "re_up_pdpa":3,
                                                                    "archive_pdpa":4,
                                                                    "exempted_crm":5}))\
                                .loc[:,"recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                                              (df.loc[:,"ix_complete"] == "Complete") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                        "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                                       (df.loc[:,"ix_complete"] == "Complete") & 
                                                       (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                                    "- 3/3 Sections Done \n" +
                                    "- Complete Result Uploaded \n" +
                                    "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                                                (df.loc[:,"ix_complete"] == "Complete") & 
                                                                (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                         df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                 (df.loc[:,"ix_complete"] == "Complete") & 
                                 (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "payment_lab", "pdpa_1", "miss_wrong_diag")],
                        df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                (df.loc[:,"ix_complete"] == "Complete") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
        if len(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                       (df.loc[:,"ix_complete"] == "No UFEME"))]) >=1:
            for recommendation in df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                          (df.loc[:,"ix_complete"] == "No UFEME"))]\
                                    .sort_values("recommendation", 
                                                 key = lambda x: x.map({"pay":1,
                                                                        "verbal":2,
                                                                        "re_up_pdpa":3,
                                                                        "archive_pdpa":4,
                                                                        "exempted_crm":5}))\
                                    .loc[:,"recommendation"].unique():
                presentation("{}. {} for No UFEME claims (n = {})".format(num, recommendation,
                                                                                   len(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                                                                               (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                                                               (df.loc[:,"recommendation"] == recommendation))])),
                            "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                                           (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                           (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                                    "- 3/3 Sections Done \n" +
                                    "- No UFEME only (Other parameters complete) \n" +
                                    "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                                                (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                                (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                            df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                    (df.loc[:,"ix_complete"] == "No UFEME") & 
                                    (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                              .loc[:,("claim_id", "provider_id", "provider_name", "hs2_created_date", "payment_hs2", "payment_lab", "pdpa_1", "miss_wrong_diag", "ix_justification")],
                            df.loc[((df.loc[:,"slide_type"] == "pdpa_issue") & 
                                    (df.loc[:,"ix_complete"] == "No UFEME") & 
                                    (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
                num += 1
                
                
    # For diagnosis issue
    elif slide_types == "diagnosis_issue":
        num = 1
        for recommendation in df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                      (df.loc[:,"ix_complete"] == "Complete"))]\
                                .sort_values("recommendation", 
                                             key = lambda x: x.map({"pay":1,
                                                                    "exempted":2}))\
                                .loc[:,"recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                                              (df.loc[:,"ix_complete"] == "Complete") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                         "- Complete PDPA/ Incomplete PDPA (No Date Only) \n" +
                         "- 3/3 Sections Done \n" +
                         "- Complete Result Uploaded \n" +
                         "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                                                (df.loc[:,"ix_complete"] == "Complete") & 
                                                                (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                         df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                 (df.loc[:,"ix_complete"] == "Complete") & 
                                 (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "payment_lab", "miss_wrong_diag", "normal_diag")],
                        df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                (df.loc[:,"ix_complete"] == "Complete") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
        if len(df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                       (df.loc[:,"ix_complete"] == "No UFEME"))]) >= 1:
            for recommendation in df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                      (df.loc[:,"ix_complete"] == "No UFEME"))]\
                                    .sort_values("recommendation", 
                                                  key = lambda x: x.map({"pay":1,
                                                                    "exempted":2}))\
                                    .loc[:,"recommendation"].unique():
                presentation("{}. {} for No UFEME (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                                              (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                             "- Complete PDPA/ Incomplete PDPA (No Date Only) \n" +
                             "- 3/3 Sections Done \n" +
                             "- No UFEME Only \n" +
                             "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                                                (df.loc[:,"ix_complete"] == "No UFEME") & 
                                                                (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                             df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                     (df.loc[:,"ix_complete"] == "No UFEME") & 
                                     (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                               .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "payment_lab", "miss_wrong_diag", "normal_diag", "ix_justification")],
                            df.loc[((df.loc[:,"slide_type"] == "diagnosis_issue") & 
                                    (df.loc[:,"ix_complete"] == "No UFEME") & 
                                    (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
            
    # For UFEME issue
    elif slide_types == "ufeme_issue":
        num = 1
        for recommendation in df.loc[df.loc[:,"slide_type"] == "ufeme_issue", "recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "ufeme_issue") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                         "- Complete PDPA/ Incomplete PDPA (No Date Only) \n" +
                         "- 3/3 Sections Done \n" +
                         "- No UFEME Only \n" +
                         "- Correct Diagnosis",
                         df.loc[(df.loc[:,"slide_type"] == "ufeme_issue") & 
                                (df.loc[:,"recommendation"] == recommendation)].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "ix_justification")],
                         df.loc[((df.loc[:,"slide_type"] == "ufeme_issue") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
            
    # For No Section K Diagnosis Issue
    elif slide_types == "no_section_k":
        num = 1
        for recommendation in df.loc[df.loc[:,"slide_type"] == "no_section_k", "recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "no_section_k") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                         "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "no_section_k") & 
                                                              (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                         "- 3/3 Sections Done \n" +
                         "- Complete Ix Result \n" +
                         "- Section K No Diagnosis",
                         df.loc[(df.loc[:,"slide_type"] == "no_section_k") & 
                                (df.loc[:,"recommendation"] == recommendation)].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "pdpa_1", "normal_diag")],
                         df.loc[((df.loc[:,"slide_type"] == "no_section_k") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
            
    # For Incomplete Section Issue
    elif slide_types == "incomplete_section":
        presentation("To Delete (n = {})".format(len(df.loc[df.loc[:,"slide_type"] == "incomplete_section"])),
                     "- {} \n".format(tuple(df.loc[df.loc[:,"slide_type"] == "incomplete_section", "pdpa_acceptance"].unique().transpose())) + 
                     "- 0 Sections Done \n" +
                     "- {} \n".format(tuple(df.loc[df.loc[:,"slide_type"] == "incomplete_section", "ix_complete"].unique().transpose())),
                     df.loc[df.loc[:,"slide_type"] == "incomplete_section"].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                       .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "pdpa_1")],
                     df.loc[df.loc[:,"slide_type"] == "incomplete_section", "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
        
    # For Incomplete Result Issue
    elif slide_types == "incomplete_result":
        num = 1
        for recommendation in df.loc[df.loc[:,"slide_type"] == "incomplete_result", "recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "incomplete_result") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                         "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "incomplete_result") & 
                                                        (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                         "- 3/3 Sections Done \n" +
                         "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "incomplete_result") & 
                                                        (df.loc[:,"recommendation"] == recommendation)), "ix_complete"].unique().transpose())) +
                         "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "incomplete_result") & 
                                                     (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                         df.loc[(df.loc[:,"slide_type"] == "incomplete_result") & 
                                (df.loc[:,"recommendation"] == recommendation)].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "pdpa_1", "ix_complete", "ix_justification")],
                         df.loc[((df.loc[:,"slide_type"] == "incomplete_result") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
            
    # For ix_issue Claims
    elif slide_types == "ix_issue":
        num = 1
        for recommendation in df.loc[df.loc[:,"slide_type"] == "ix_issue"]\
                                .sort_values("recommendation", 
                                                 key = lambda x: x.map({"pay":1,
                                                                        "verbal":2,
                                                                        "re_up_pdpa":3,
                                                                        "archive_pdpa":4,
                                                                        "exempted_crm":5}))\
                                .loc[:,"recommendation"].unique():
            presentation("{}. {} (n = {})".format(num, recommendation,
                                                  len(df.loc[((df.loc[:,"slide_type"] == "ix_issue") & 
                                                              (df.loc[:,"recommendation"] == recommendation))])),
                         "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "ix_issue") & 
                                                        (df.loc[:,"recommendation"] == recommendation)), "pdpa_acceptance"].unique().transpose())) +
                         "- 3/3 Sections Done \n" +
                         "- {} \n".format(tuple(df.loc[((df.loc[:,"slide_type"] == "ix_issue") & 
                                                        (df.loc[:,"recommendation"] == recommendation)), "ix_complete"].unique().transpose())) +
                         "- {}".format(tuple(df.loc[((df.loc[:,"slide_type"] == "ix_issue") & 
                                                     (df.loc[:,"recommendation"] == recommendation)), "diagnosis2"].unique().transpose())),
                         df.loc[(df.loc[:,"slide_type"] == "ix_issue") & 
                                (df.loc[:,"recommendation"] == recommendation)].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "payment_hs2", "pdpa_1", "ix_justification")],
                         df.loc[((df.loc[:,"slide_type"] == "ix_issue") & 
                                (df.loc[:,"recommendation"] == recommendation)), "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
            num += 1
    # For Delete Claims
    elif slide_types == "delete":
        presentation("To Delete (n= {})".format(len(df.loc[df.loc[:,"slide_type"] == "delete"])),
                     "- {} \n".format(tuple(df.loc[df.loc[:,"slide_type"] == "delete" , "pdpa_acceptance"].unique().transpose())) +
                     "- {} Sections Done \n".format(tuple(df.loc[df.loc[:,"slide_type"] == "delete", "section_done"].unique().transpose())) +
                     "- {} \n".format(tuple(df.loc[df.loc[:,"slide_type"] == "delete", "ix_complete"].unique().transpose())) +
                     "- {}".format(tuple(df.loc[df.loc[:,"slide_type"] == "delete", "diagnosis2"].unique().transpose())),
                     df.loc[df.loc[:,"slide_type"] == "delete"].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                       .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "section_done", "pdpa_1", "ix_complete")],
                     df.loc[df.loc[:,"slide_type"] == "delete", "tcmc_recommendation"].reset_index().loc[0,"tcmc_recommendation"])
        
    # For undecisive Claims
    elif slide_types == "issue":
        for recommendation in df.loc[df.loc[:,"slide_type"] == "issue", "recommendation"].unique():
            st.write("{}".format(recommendation))
            st.dataframe(df.loc[((df.loc[:,"slide_type"] == "issue") & 
                                 (df.loc[:,"recommendation"] == recommendation))].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                           .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date", "section_done", "pdpa_1", "ix_complete")])
        
    # For Paid Claims
    elif slide_types == "paid":
        st.write("Paid (n = {})".format(len(df.loc[df.loc[:,"slide_type"] == "paid"])))
        st.table(df.loc[df.loc[:,"slide_type"] == "paid"].sort_values(["provider_id", "hs1_created_date"]).reset_index()\
                   .loc[:,("claim_id", "provider_id", "provider_name", "hs1_created_date")])