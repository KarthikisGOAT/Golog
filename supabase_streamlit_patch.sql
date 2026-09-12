
-- Karthik Streamlit login patch
-- Allows the app to translate username / Employee ID to the
-- email used by Supabase Auth without exposing profile rows.

create or replace function public.get_auth_email_by_username(p_username text)
returns text
language sql
security definer
set search_path = public
as $$
    select p.email
    from public.profiles p
    where lower(p.username) = lower(p_username)
      and p.active = true
    limit 1;
$$;

revoke all on function public.get_auth_email_by_username(text) from public;
grant execute on function public.get_auth_email_by_username(text) to anon, authenticated;

-- The app records status changes in job_status_history.
-- Add this policy so authenticated users can insert history for jobs
-- they are allowed to update.
create policy "Users can insert permitted job history"
on public.job_status_history
for insert
to authenticated
with check (
    changed_by = (select auth.uid())
    and exists (
        select 1
        from public.jobs j
        where j.id = job_status_history.job_id
    )
);
