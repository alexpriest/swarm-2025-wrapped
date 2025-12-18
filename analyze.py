"""
Swarm Wrapped - Analysis Module

Processes raw Foursquare check-in data and generates statistics for the wrapped report.
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import math


def analyze_checkins(checkins: list) -> dict:
    """
    Analyze a list of Foursquare check-ins and return statistics.

    Args:
        checkins: List of check-in objects from Foursquare API

    Returns:
        Dictionary with all computed statistics
    """
    if not checkins:
        return {}

    stats = {}

    # Basic counts
    stats["total_checkins"] = len(checkins)

    # Unique venues
    venues = {}
    venue_counts = Counter()
    category_counts = Counter()
    city_counts = Counter()
    country_counts = Counter()

    # Time distributions
    hourly = Counter()
    daily = Counter()
    monthly = Counter()

    # Date tracking for streaks
    checkin_dates = set()
    checkins_per_day = Counter()

    # Friends
    friend_counts = Counter()
    checkins_with_friends = 0

    # Shouts and photos
    checkins_with_shouts = 0
    total_photos = 0

    # Location tracking for map
    map_points = defaultdict(list)

    for checkin in checkins:
        venue = checkin.get("venue", {})
        venue_id = venue.get("id", "unknown")
        venue_name = venue.get("name", "Unknown Venue")

        # Count venue visits
        venue_counts[venue_name] += 1

        # Store venue info
        if venue_id not in venues:
            location = venue.get("location", {})
            categories = venue.get("categories", [])
            primary_category = categories[0]["name"] if categories else "Other"

            venues[venue_id] = {
                "name": venue_name,
                "category": primary_category,
                "city": location.get("city", "Unknown"),
                "state": location.get("state", ""),
                "country": location.get("country", "Unknown"),
                "lat": location.get("lat"),
                "lng": location.get("lng")
            }

        venue_info = venues[venue_id]

        # Count categories
        category_counts[venue_info["category"]] += 1

        # Count cities
        city_key = venue_info["city"]
        if venue_info["state"]:
            city_key = f"{venue_info['city']}, {venue_info['state']}"
        elif venue_info["country"] != "United States":
            city_key = f"{venue_info['city']}, {venue_info['country']}"
        city_counts[city_key] += 1

        # Count countries
        country_counts[venue_info["country"]] += 1

        # Time analysis
        created_at = checkin.get("createdAt", 0)
        dt = datetime.fromtimestamp(created_at)

        hourly[dt.hour] += 1
        daily[dt.strftime("%A")] += 1
        monthly[dt.strftime("%b")] += 1

        date_str = dt.strftime("%Y-%m-%d")
        checkin_dates.add(date_str)
        checkins_per_day[date_str] += 1

        # Friends
        with_friends = checkin.get("with", [])
        if with_friends:
            checkins_with_friends += 1
            for friend in with_friends:
                friend_name = f"{friend.get('firstName', '')} {friend.get('lastName', '')}".strip()
                if friend_name:
                    friend_counts[friend_name] += 1

        # Shouts and photos
        if checkin.get("shout"):
            checkins_with_shouts += 1
        total_photos += len(checkin.get("photos", {}).get("items", []))

        # Map points
        if venue_info["lat"] and venue_info["lng"]:
            lat_rounded = round(venue_info["lat"], 4)
            lng_rounded = round(venue_info["lng"], 4)
            map_points[(lat_rounded, lng_rounded)].append(f"{venue_name}(1)")

    # Top venues
    stats["unique_venues"] = len(venues)
    stats["top_venues"] = [
        {
            "name": name,
            "count": count,
            **{k: v for k, v in venues.get(
                next((vid for vid, v in venues.items() if v["name"] == name), {}
            ), {}).items() if k != "name"}
        }
        for name, count in venue_counts.most_common(10)
    ]

    # Fix top_venues to include venue details
    top_venues_fixed = []
    for name, count in venue_counts.most_common(10):
        venue_data = next((v for v in venues.values() if v["name"] == name), {})
        top_venues_fixed.append({
            "name": name,
            "count": count,
            "category": venue_data.get("category", ""),
            "city": venue_data.get("city", ""),
            "state": venue_data.get("state", ""),
            "country": venue_data.get("country", "")
        })
    stats["top_venues"] = top_venues_fixed

    # Top categories
    stats["top_categories"] = [
        {"name": name, "count": count}
        for name, count in category_counts.most_common(10)
    ]
    stats["unique_categories"] = len(category_counts)

    # Top cities
    stats["top_cities"] = [
        {"name": name, "count": count}
        for name, count in city_counts.most_common(10)
    ]
    stats["unique_cities"] = len(city_counts)

    # Countries
    stats["countries"] = [
        {"name": name, "count": count}
        for name, count in country_counts.most_common()
    ]

    # Time distributions
    stats["hourly_distribution"] = {str(h): hourly.get(h, 0) for h in range(24)}
    stats["monthly_distribution"] = {
        month: monthly.get(month, 0)
        for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    }

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    stats["daily_distribution"] = {day: daily.get(day, 0) for day in day_order}

    # Peak times
    stats["peak_hour"] = max(hourly, key=hourly.get) if hourly else 0
    stats["peak_hour_formatted"] = f"{stats['peak_hour']}am" if stats["peak_hour"] < 12 else f"{stats['peak_hour']-12 or 12}pm"
    stats["busiest_day"] = max(daily, key=daily.get) if daily else "Unknown"
    stats["busiest_month"] = max(monthly, key=monthly.get) if monthly else "Unknown"

    # Activity stats
    sorted_dates = sorted(checkin_dates)
    stats["days_active"] = len(checkin_dates)

    if sorted_dates:
        first_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
        last_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
        total_days = (last_date - first_date).days + 1
        stats["total_days_2025"] = total_days
        stats["activity_percentage"] = round(len(checkin_dates) / total_days * 100, 1) if total_days > 0 else 0
    else:
        stats["total_days_2025"] = 0
        stats["activity_percentage"] = 0

    stats["avg_checkins_per_active_day"] = round(len(checkins) / len(checkin_dates), 1) if checkin_dates else 0

    # Busiest day
    if checkins_per_day:
        max_day = max(checkins_per_day, key=checkins_per_day.get)
        stats["max_checkins_day"] = max_day
        stats["max_checkins_count"] = checkins_per_day[max_day]
    else:
        stats["max_checkins_day"] = ""
        stats["max_checkins_count"] = 0

    # Streak calculation
    stats["longest_streak"] = calculate_longest_streak(sorted_dates)

    # Friends stats
    stats["checkins_with_friends"] = checkins_with_friends
    stats["friend_percentage"] = round(checkins_with_friends / len(checkins) * 100, 1) if checkins else 0
    stats["top_friends"] = [
        {"name": name, "count": count}
        for name, count in friend_counts.most_common(5)
    ]

    # Solo stats
    stats["solo_checkins"] = len(checkins) - checkins_with_friends
    stats["solo_percentage"] = round(stats["solo_checkins"] / len(checkins) * 100, 1) if checkins else 0

    # Shouts and photos
    stats["checkins_with_shouts"] = checkins_with_shouts
    stats["shout_percentage"] = round(checkins_with_shouts / len(checkins) * 100, 1) if checkins else 0
    stats["total_photos"] = total_photos

    # Time personality
    morning = sum(hourly.get(h, 0) for h in range(5, 12))
    afternoon = sum(hourly.get(h, 0) for h in range(12, 17))
    evening = sum(hourly.get(h, 0) for h in range(17, 21))
    night = sum(hourly.get(h, 0) for h in list(range(21, 24)) + list(range(0, 5)))

    stats["time_of_day"] = {
        "morning": morning,
        "afternoon": afternoon,
        "evening": evening,
        "night": night
    }

    max_time = max([("morning", morning), ("afternoon", afternoon), ("evening", evening), ("night", night)], key=lambda x: x[1])
    time_personalities = {
        "morning": "Early Bird",
        "afternoon": "Day Explorer",
        "evening": "Evening Wanderer",
        "night": "Night Owl"
    }
    stats["time_personality"] = time_personalities.get(max_time[0], "Explorer")

    # Weekend vs weekday
    weekend = daily.get("Saturday", 0) + daily.get("Sunday", 0)
    weekday = sum(daily.get(d, 0) for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    total = weekend + weekday
    stats["weekend_percentage"] = round(weekend / total * 100, 1) if total > 0 else 0
    stats["weekday_percentage"] = round(weekday / total * 100, 1) if total > 0 else 0

    # First and last check-in
    if checkins:
        first_checkin = min(checkins, key=lambda x: x.get("createdAt", 0))
        last_checkin = max(checkins, key=lambda x: x.get("createdAt", 0))

        first_dt = datetime.fromtimestamp(first_checkin.get("createdAt", 0))
        last_dt = datetime.fromtimestamp(last_checkin.get("createdAt", 0))

        stats["first_checkin"] = {
            "venue": first_checkin.get("venue", {}).get("name", "Unknown"),
            "date": first_dt.strftime("%B %d, %Y"),
            "time": first_dt.strftime("%I:%M %p")
        }
        stats["last_checkin"] = {
            "venue": last_checkin.get("venue", {}).get("name", "Unknown"),
            "date": last_dt.strftime("%B %d, %Y"),
            "time": last_dt.strftime("%I:%M %p")
        }

    # Map data (grouped by location)
    stats["map_points"] = [
        {"lat": lat, "lng": lng, "v": ",".join(venues)}
        for (lat, lng), venues in map_points.items()
    ]

    return stats


def calculate_longest_streak(sorted_dates: list) -> int:
    """Calculate the longest consecutive day streak."""
    if not sorted_dates:
        return 0

    max_streak = 1
    current_streak = 1

    for i in range(1, len(sorted_dates)):
        prev_date = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d")
        curr_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d")

        if (curr_date - prev_date).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak
