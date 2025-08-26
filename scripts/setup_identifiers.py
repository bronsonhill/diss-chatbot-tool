#!/usr/bin/env python3
"""
Setup script for DiSS Chatbot MongoDB identifiers

This script helps administrators set up valid user identifiers in the MongoDB database.
"""

import os
import sys
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def setup_identifiers():
    """Set up valid identifiers in MongoDB"""
    
    # Get MongoDB connection string
    mongodb_uri = input("Enter your MongoDB connection string: ").strip()
    
    if not mongodb_uri:
        print("❌ MongoDB connection string is required")
        return
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        db = client.diss_chatbot
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        
        # Create valid_identifiers collection if it doesn't exist
        if 'valid_identifiers' not in db.list_collection_names():
            db.create_collection('valid_identifiers')
            print("✅ Created valid_identifiers collection")
        
        # Add identifiers
        print("\nEnter user identifiers (one per line, press Enter twice to finish):")
        identifiers = []
        
        while True:
            identifier = input("Identifier: ").strip()
            if not identifier:
                break
            identifiers.append({"identifier": identifier})
        
        if identifiers:
            # Insert identifiers
            result = db.valid_identifiers.insert_many(identifiers)
            print(f"✅ Successfully added {len(result.inserted_ids)} identifiers")
            
            # Display all identifiers
            print("\nCurrent valid identifiers:")
            for doc in db.valid_identifiers.find():
                print(f"  - {doc['identifier']}")
        else:
            print("❌ No identifiers provided")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def list_identifiers():
    """List all current valid identifiers"""
    
    mongodb_uri = input("Enter your MongoDB connection string: ").strip()
    
    if not mongodb_uri:
        print("❌ MongoDB connection string is required")
        return
    
    try:
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        db = client.diss_chatbot
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        
        # List identifiers
        identifiers = list(db.valid_identifiers.find())
        
        if identifiers:
            print(f"\nFound {len(identifiers)} valid identifiers:")
            for doc in identifiers:
                print(f"  - {doc['identifier']}")
        else:
            print("No identifiers found in database")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def remove_identifier():
    """Remove a specific identifier"""
    
    mongodb_uri = input("Enter your MongoDB connection string: ").strip()
    
    if not mongodb_uri:
        print("❌ MongoDB connection string is required")
        return
    
    identifier = input("Enter identifier to remove: ").strip()
    
    if not identifier:
        print("❌ Identifier is required")
        return
    
    try:
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        db = client.diss_chatbot
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        
        # Remove identifier
        result = db.valid_identifiers.delete_one({"identifier": identifier})
        
        if result.deleted_count > 0:
            print(f"✅ Successfully removed identifier: {identifier}")
        else:
            print(f"❌ Identifier not found: {identifier}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    print("DiSS Chatbot - MongoDB Identifier Setup")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Add new identifiers")
        print("2. List current identifiers")
        print("3. Remove an identifier")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            setup_identifiers()
        elif choice == "2":
            list_identifiers()
        elif choice == "3":
            remove_identifier()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main()
