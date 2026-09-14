df['tenure_days'] = np.where(df['cancellation_date'].notna, 
            (df['cancellation_date'] - df['subscription_start_date']).dt.day,
            (today - df['subscription_start_date']).dt.day

    )