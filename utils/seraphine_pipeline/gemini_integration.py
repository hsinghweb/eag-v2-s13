"""
Gemini Integration Utility
Handles integration of Gemini LLM results into seraphine structure
"""
from .helpers import debug_print

def integrate_llm_results(seraphine_analysis, llm_results):
    """
    Integrate Gemini results into seraphine structure at individual bbox level
    """
    if not gemini_results or not gemini_results.get('images'):
        debug_print("⚠️  No Gemini results to integrate")
        return seraphine_analysis
    
    # ✅ ALWAYS PRINT - Show integration start
    print("\n🤖 [LLM] ===== INTEGRATING LLM RESULTS =====")
    print("🤖 [LLM] Mapping LLM icon names to seraphine groups...")
    
    debug_print("\n🔗 Integrating LLM results into seraphine structure...")
    
    # Create mapping from ALL LLM results across all images
    id_to_llm = {}
    
    for image_result in llm_results['images']:
        if image_result['analysis_success'] and image_result.get('icons'):
            for icon in image_result['icons']:
                icon_id = icon.get('id')  # Like "H1_1", "H12_3", etc.
                if icon_id:
                    id_to_llm[icon_id] = {
                        'icon_name': icon.get('name', 'unknown'),
                        'brief': icon.get('usage', 'No description'),
                        'enabled': icon.get('enabled', True),
                        'interactive': icon.get('interactive', True),
                        'type': icon.get('type', 'icon')  # New field
                    }
                    # Show first few mappings
                    if len(id_to_llm) <= 5:
                        print(f"🤖 [LLM]   Mapping: {icon_id} → '{icon.get('name', 'unknown')}'")
    
    print(f"🤖 [LLM] ✅ Created {len(id_to_llm)} icon name mappings from LLM")
    debug_print(f"   📋 Found {len(id_to_llm)} LLM mappings to integrate")
    
    # Integrate results into seraphine bbox_processor
    bbox_processor = seraphine_analysis['bbox_processor']
    total_integrated = 0
    
    for group_id, boxes in bbox_processor.final_groups.items():
        # Process each box in the group
        for i, bbox in enumerate(boxes):
            item_id = f"{group_id}_{i+1}"  # H1_1, H1_2, etc.
            
            if item_id in id_to_gemini:
                # Found exact match!
                gemini_data = id_to_gemini[item_id]
                bbox.g_icon_name = gemini_data['icon_name']
                bbox.g_brief = gemini_data['brief']
                bbox.g_enabled = gemini_data['enabled']
                bbox.g_interactive = gemini_data['interactive']
                bbox.g_type = gemini_data['type']  # New field
                total_integrated += 1
                
                if total_integrated <= 5:  # Show first 5 for debugging
                    debug_print(f"   ✅ {item_id}: '{gemini_data['icon_name']}' - {gemini_data['brief'][:50]}...")
            else:
                # Default values if no Gemini result available
                bbox.g_icon_name = 'unanalyzed'
                bbox.g_brief = 'Not analyzed by Gemini'
    
    total_elements = sum(len(boxes) for boxes in bbox_processor.final_groups.values())
    print(f"🤖 [GEMINI] ✅ Integrated: {total_integrated}/{total_elements} elements updated with Gemini names")
    if total_integrated < total_elements:
        print(f"🤖 [GEMINI] ⚠️  {total_elements - total_integrated} elements did NOT get Gemini names (will show 'unanalyzed')")
        print(f"🤖 [GEMINI]    This may indicate ID mismatch between Gemini results and seraphine groups")
    
    debug_print(f"✅ Integrated Gemini results: {total_integrated}/{total_elements} items updated")
    
    # 🎯 NEW: REGENERATE SERAPHINE_GEMINI_GROUPS WITH UPDATED DATA
    from .pipeline_exporter import create_enhanced_seraphine_structure
    
    # Get the merged_detections from analysis for proper ID lookup
    merged_detections = seraphine_analysis.get('original_merged_detections', [])
    
    # Create the enhanced structure with integrated Gemini data
    seraphine_gemini_groups = create_enhanced_seraphine_structure(
        seraphine_analysis, 
        merged_detections
    )
    
    # Add it to the analysis
    seraphine_analysis['seraphine_gemini_groups'] = seraphine_gemini_groups
    
    print(f"🤖 [LLM] 🎯 Generated seraphine_gemini_groups with {len(seraphine_gemini_groups)} groups")
    print("🤖 [LLM] ===== INTEGRATION COMPLETE =====\n")
    
    debug_print(f"🎯 Generated seraphine_gemini_groups with {len(seraphine_gemini_groups)} groups")
    
    return seraphine_analysis


# Keep backward compatibility
def integrate_gemini_results(seraphine_analysis, gemini_results):
    """Backward compatibility wrapper - redirects to integrate_llm_results"""
    return integrate_llm_results(seraphine_analysis, gemini_results)

async def run_llm_analysis(seraphine_analysis, grouped_image_paths, image_path, config):
    """
    Run LLM analysis with optimized image sharing - supports both Gemini and Groq
    """
    # Determine which LLM to use
    llm_provider = config.get("llm_provider", "groq").lower()  # Default to Groq
    groq_enabled = config.get("groq_enabled", True)  # Default to enabled
    gemini_enabled = config.get("gemini_enabled", False)
    
    # Auto-detect: if Groq is enabled, use it; otherwise try Gemini
    if groq_enabled:
        llm_provider = "groq"
    elif gemini_enabled:
        llm_provider = "gemini"
    else:
        print("❌ [LLM] No LLM provider enabled!")
        print("   Set 'groq_enabled': true or 'gemini_enabled': true in config.json")
        return None
    
    # ✅ ALWAYS PRINT - Not just in debug mode
    print("\n" + "="*80)
    if llm_provider == "groq":
        print("🚀 [GROQ] ===== GROQ LLM ANALYSIS STARTING =====")
    else:
        print("🤖 [GEMINI] ===== GEMINI LLM ANALYSIS STARTING =====")
    print("="*80)
    
    print(f"📸 Analyzing screenshot: {image_path}")
    
    # Check for API key
    import os
    if llm_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("🚀 [GROQ] ❌ ERROR: GROQ_API_KEY environment variable is NOT set!")
            print("🚀 [GROQ]    Set it with: $env:GROQ_API_KEY = 'your-key' (PowerShell)")
            print("🚀 [GROQ]    Or create .env file with: GROQ_API_KEY=your-key")
            return None
        else:
            print(f"🚀 [GROQ] ✅ GROQ_API_KEY found (length: {len(api_key)} chars)")
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("🤖 [GEMINI] ❌ ERROR: GEMINI_API_KEY environment variable is NOT set!")
            print("🤖 [GEMINI]    Set it with: $env:GEMINI_API_KEY = 'your-key' (PowerShell)")
            print("🤖 [GEMINI]    Or create .env file with: GEMINI_API_KEY=your-key")
            return None
        else:
            print(f"🤖 [GEMINI] ✅ GEMINI_API_KEY found (length: {len(api_key)} chars)")
    
    debug_print(f"\n{'🚀' if llm_provider == 'groq' else '🤖'} Step 4: {llm_provider.upper()} LLM Analysis (Optimized Image Sharing)")
    debug_print("=" * 70)
    
    try:
        import os
        
        output_dir = config.get("output_dir", "outputs")
        filename_base = os.path.splitext(os.path.basename(image_path))[0]
        
        # Initialize analyzer based on provider
        if llm_provider == "groq":
            from .groq_analyzer import GroqIconAnalyzer
            analyzer = GroqIconAnalyzer(
                prompt_path=config.get("groq_prompt_path") or config.get("gemini_prompt_path"),  # Use same prompt
                output_dir=output_dir,
                max_concurrent_requests=config.get("groq_max_concurrent", 4),
                save_results=config.get("save_groq_json", True),
                model=config.get("groq_model", "llama-3.3-70b-versatile")
            )
        else:
            from .gemini_analyzer import GeminiIconAnalyzer
            analyzer = GeminiIconAnalyzer(
                prompt_path=config.get("gemini_prompt_path"),  # Pass None to use default
                output_dir=output_dir,
                max_concurrent_requests=config.get("gemini_max_concurrent", 4),
                save_results=config.get("save_gemini_json", True)
            )
        
        # Use direct image mode for optimized sharing
        use_direct_images = config.get("groq_return_images_b64", True) if llm_provider == "groq" else config.get("gemini_return_images_b64", True)
        
        if use_direct_images:
            debug_print("   📸 Using optimized direct image mode (faster, less I/O)")
            
            from .seraphine_generator import FinalGroupImageGenerator
            
            # Create generator to get direct images
            final_group_generator = FinalGroupImageGenerator(
                output_dir=output_dir,
                save_mapping=False  # Don't save files, just get images
            )
            
            # Get direct images using the correct method
            result = final_group_generator.create_grouped_images(
                image_path=image_path,
                seraphine_analysis=seraphine_analysis,
                filename_base=filename_base,
                return_direct_images=True
            )
            
            # Extract direct images from result
            direct_images = result.get('direct_images', [])
            
            if not direct_images or len(direct_images) == 0:
                provider_name = "Groq" if llm_provider == "groq" else "Gemini"
                print(f"{'🚀 [GROQ]' if llm_provider == 'groq' else '🤖 [GEMINI]'} ❌ ERROR: No images generated for {provider_name} analysis!")
                print(f"{'🚀 [GROQ]' if llm_provider == 'groq' else '🤖 [GEMINI]'}    This means no groups were available to analyze")
                print(f"{'🚀 [GROQ]' if llm_provider == 'groq' else '🤖 [GEMINI]'}    Check why all groups have explore=False")
                return None
            
            provider_emoji = "🚀 [GROQ]" if llm_provider == "groq" else "🤖 [GEMINI]"
            print(f"{provider_emoji} 🖼️  Generated {len(direct_images)} grouped images for analysis")
            print(f"{provider_emoji} 📋 Each image contains UI elements with labeled IDs (H1_1, H2_3, etc.)")
            debug_print(f"   🖼️  Generated {len(direct_images)} direct images for {llm_provider} analysis")
            
            # Analyze with direct images (no file I/O)
            print(f"{provider_emoji} 🚀 Starting {llm_provider.upper()} API calls for {len(direct_images)} images...")
            llm_results = await analyzer.analyze_grouped_images(
                grouped_image_paths=None,
                filename_base=filename_base,
                direct_images=direct_images
            )
        else:
            debug_print("   📁 Using file mode (traditional)")
            # Use traditional file mode
            llm_results = await analyzer.analyze_grouped_images(
                grouped_image_paths=grouped_image_paths,
                filename_base=filename_base,
                direct_images=None
            )
        
        # ✅ ALWAYS PRINT - Show summary
        provider_emoji = "🚀 [GROQ]" if llm_provider == "groq" else "🤖 [GEMINI]"
        provider_name = "GROQ" if llm_provider == "groq" else "GEMINI"
        print("\n" + "="*80)
        print(f"{provider_emoji} ===== {provider_name} ANALYSIS COMPLETE =====")
        print(f"{provider_emoji} ✅ Successfully analyzed: {llm_results['successful_analyses']}/{llm_results['total_images_analyzed']} images")
        print(f"{provider_emoji} 🎯 Total icons/buttons identified: {llm_results['total_icons_found']}")
        print(f"{provider_emoji} ⏱️  Total analysis time: {llm_results['analysis_duration_seconds']:.2f}s")
        print("="*80 + "\n")
        
        debug_print(f"✅ {llm_provider} analysis complete:")
        debug_print(f"   🖼️  Analyzed: {llm_results['successful_analyses']}/{llm_results['total_images_analyzed']} images")
        debug_print(f"   🎯 Total icons found: {llm_results['total_icons_found']}")
        debug_print(f"   ⏱️  Analysis time: {llm_results['analysis_duration_seconds']:.2f}s")
        
        return llm_results
        
    except ImportError as e:
        provider_emoji = "🚀 [GROQ]" if llm_provider == "groq" else "🤖 [GEMINI]"
        provider_name = "Groq" if llm_provider == "groq" else "Gemini"
        package_name = "groq" if llm_provider == "groq" else "google-genai"
        print(f"{provider_emoji} ❌ ERROR: {provider_name} analyzer not available (missing dependencies)")
        print(f"{provider_emoji}    Install with: pip install {package_name}")
        debug_print(f"❌ {provider_name} analyzer not available (missing dependencies)")
        return None
    except Exception as e:
        provider_emoji = "🚀 [GROQ]" if llm_provider == "groq" else "🤖 [GEMINI]"
        print(f"{provider_emoji} ❌ ERROR: {llm_provider} analysis failed: {str(e)}")
        import traceback
        print(f"{provider_emoji} Full error traceback:")
        traceback.print_exc()
        debug_print(f"❌ {llm_provider} analysis failed: {str(e)}")
        return None


# Keep backward compatibility
async def run_gemini_analysis(seraphine_analysis, grouped_image_paths, image_path, config):
    """Backward compatibility wrapper - redirects to run_llm_analysis"""
    return await run_llm_analysis(seraphine_analysis, grouped_image_paths, image_path, config)
