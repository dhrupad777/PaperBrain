'use client';

import { Button } from '@/components/ui/button';
import { User, LogIn, LogOut } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useState } from 'react';

export function AuthButton() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Placeholder for Firebase Auth logic
  const handleSignIn = () => setIsLoggedIn(true);
  const handleSignOut = () => setIsLoggedIn(false);

  if (isLoggedIn) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="secondary" size="icon" className="rounded-full">
            <User className="h-5 w-5" />
            <span className="sr-only">Toggle user menu</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>My Account</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Settings</DropdownMenuItem>
          <DropdownMenuItem>Support</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleSignOut}>
            <LogOut className="mr-2 h-4 w-4" />
            <span>Log out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <Button onClick={handleSignIn}>
      <LogIn className="mr-2 h-4 w-4" />
      Sign In
    </Button>
  );
}
